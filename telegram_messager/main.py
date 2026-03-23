

from typing import Union
from typing_extensions import TypeAlias, Optional, Dict

import os
import sys
from pathlib import Path
import argparse

import json
import requests


PathLike: TypeAlias = Union[str, os.PathLike]

TOKEN_NAME_DEFAULT = 'TELEGRAM_MESSAGER_BOT_TOKEN'
CHAT_ID_NAME_DEFAULT = 'TELEGRAM_MESSAGER_CHAR_ID'
TIMEOUT_DEFAULT = 'TELEGRAM_MESSAGER_TIMEOUT'

DEFAULT_API = 'https://api.telegram.org'


def read_text(result_path: PathLike, encoding: str = 'utf-8') -> str:
    """reads file text"""
    return Path(result_path).read_text(encoding=encoding, errors='ignore')


def read_env_var(name: str, non_empty: bool = False) -> str:
    assert name
    v = os.getenv(name, None)
    assert v is not None, f"not found variable in env: {name}"
    if non_empty and not v:
        raise ValueError(f"empty value for env variable {name}")
    return v


def _preprocess_text(text: str) -> str:
    t = text.replace('<', '').replace('>', '')
    if len(t) >= 1024:
        return t[:1021] + '...'
    return t


class TelegramMessager:
    def __init__(
        self, 
        token: str, 
        chatid: str, 
        timeout: Optional[float] = None, 
        headers: Optional[Dict[str, str]] = None,
        api_path: str = DEFAULT_API,
    ):
        assert token and chatid, (token, chatid)
        self.bot_token = token.strip()
        self.bot_chatId = chatid.strip()

        self.timeout = float(timeout) if timeout else None
        assert self.timeout is None or self.timeout >= 0, self.timeout
        
        self.headers = headers or {}
        
        self.api = api_path.rstrip('/')
        assert self.api, f'bad api: {api_path}'

    @property
    def _prefix(self):
        return f'{self.api}/bot{self.bot_token}/'
    
    @property
    def _kwargs(self):
        return dict(
            timeout=self.timeout,
            headers=self.headers,
        )

    #region CONSTRUCTORS
    @staticmethod
    def from_env(bot_token_name: str = '', chat_id_name: str = '', timeout_name: str = ''):
        """
        creates the object reading credentials from environment using input names

        if names are empty, uses default names
        """
        return TelegramMessager(
            token=read_env_var(bot_token_name or TOKEN_NAME_DEFAULT, non_empty=True),
            chatid=read_env_var(chat_id_name or CHAT_ID_NAME_DEFAULT, non_empty=True),
            timeout=read_env_var(timeout_name or TIMEOUT_DEFAULT, non_empty=False),
        )

    @staticmethod
    def from_token_chatid_pair_string(s: str):
        return TelegramMessager(*s.strip().split())

    @staticmethod
    def from_file(credentials_file: PathLike):
        """
        loads credentials from file with string like
            token chat_id
        """
        return TelegramMessager.from_token_chatid_pair_string(read_text(credentials_file))

    #endregion

    #region SEND METHODS
    def send_text(self, text: str):
        url_req = self._prefix + f"sendMessage?chat_id={self.bot_chatId}&text={_preprocess_text(text)}"
        results = requests.get(
            url_req, **self._kwargs
        )
        return results.json()

    def send_document(self, path: PathLike, caption: str = ''):

        send_document = self._prefix + 'sendDocument?'
        data = {
          'chat_id': self.bot_chatId,
          'parse_mode': 'HTML',
          'caption': _preprocess_text(caption)
        }
        # Need to pass the document field in the files dict
        files = {
            'document': open(path, 'rb')
        }

        r = requests.post(
            send_document, 
            data=data, files=files, stream=True, 
            **self._kwargs
        )
        # print(r.url)

        return r.json()

    def send_documents(self, *paths: PathLike, caption: str = ''):
        assert paths

        media = [
            {"type": "document", "media": f"attach://{i}"}
            for i in range(len(paths))
        ]
        if caption:
            media[-1]['caption'] = _preprocess_text(caption)

        files = {
            str(i): open(p, 'rb')
            for i, p in enumerate(paths)
        }

        r = requests.post(
            self._prefix + "sendMediaGroup",
            data={
                "chat_id": self.bot_chatId,
                "media": json.dumps(media)
            },
            files=files,
            **self._kwargs
        )

        return r.json()

    def send(self, *files: PathLike, text: str = ''):
        """universal function which sends text or files or both depends on existence"""
        assert text or files, 'nothing to send'

        if not files:
            return self.send_text(text)

        if len(files) == 1:
            return self.send_document(files[0], text)

        return self.send_documents(*files, caption=text)

    #endregion


#region CLI


class kvdictAppendAction(argparse.Action):
    """
    argparse action to split an argument into KEY=VALUE form
    on the first = and append to a dictionary.
    """
    def __call__(self, parser, args, values, option_string=None):
        assert len(values) == 1
        try:
            (k, v) = values[0].split("=", 2)
        except ValueError as ex:
            raise argparse.ArgumentError(
                self, f"could not parse argument \"{values[0]}\" as k=v format"
            )
        d = getattr(args, self.dest) or {}
        d[k] = v
        setattr(args, self.dest, d)


parser = argparse.ArgumentParser(
    prog=f"tgmg",
    description='Simplest tool to send messages using Telegram HTTP API',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument(
    '--text', '-s', action='store', type=str,
    help='text to send', default=''
)

parser.add_argument(
    '--files', '-f', action='store', type=str, nargs='+',
    help='documents to send',
)


parser.add_argument(
    '--token', '-t', action='store', type=str,
    help='bot token'
)

parser.add_argument(
    '--token-file', action='store', type=str,
    help='bot token file to read token from; will be used if no --token specified'
)

parser.add_argument(
    '--token-env-var', action='store', type=str,
    help='bot token environment variable name to read from; will be used if neither --token nor --token-file specified',
    default=TOKEN_NAME_DEFAULT
)

parser.add_argument(
    '--chat', '-c', action='store', type=str,
    help='chat id'
)

parser.add_argument(
    '--chat-file', action='store', type=str,
    help='chat id file to read the value from'
)

parser.add_argument(
    '--chat-env-var', action='store', type=str,
    help='chat id environment variable name to read from', default=CHAT_ID_NAME_DEFAULT
)

parser.add_argument(
    '--timeout', '-z', action='store', type=float,
    help='requests timeout', 
    default=None
)

parser.add_argument(
    '--api-path', '-a', action='store', type=str,
    help='telegram API path (or proxy)', 
    default=DEFAULT_API
)

parser.add_argument(
    "--headers", "-d",
    nargs=1,
    action=kvdictAppendAction,
    metavar="KEY=VALUE",
    default={},
    type=str,
    help="Extra headers",
)


def cli():

    sys.path.append(
        os.path.dirname(os.getcwd())
    )

    args = sys.argv[1:]

    parsed = parser.parse_args(args)

    assert parsed.text or parsed.files, 'nothing to send'

    if parsed.token:
        token = parsed.token
    elif parsed.token_file:
        token = read_text(parsed.token_file)
    else:
        token = read_env_var(parsed.token_env_var, non_empty=True)

    if parsed.chat:
        chat = parsed.chat
    elif parsed.chat_file:
        chat = read_text(parsed.chat_file)
    else:
        chat = read_env_var(parsed.chat_env_var, non_empty=True)

    res = TelegramMessager(
        token, chat,

        api_path=parsed.api_path,
        timeout=parsed.timeout,
        headers=parsed.headers,
    ).send(
        *(parsed.files or []), text=parsed.text
    )
    print(json.dumps(res))

    # print()


#endregion


if __name__ == '__main__':
    cli()

