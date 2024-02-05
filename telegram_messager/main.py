

from typing import Union, Optional
from typing_extensions import TypeAlias

import os
from pathlib import Path

import json
import requests


PathLike: TypeAlias = Union[str, os.PathLike]

TOKEN_NAME_DEFAULT = 'TELEGRAM_MESSAGER_BOT_TOKEN'
CHAT_ID_NAME_DEFAULT = 'TELEGRAM_MESSAGER_CHAR_ID'


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
    def __init__(self, token: str, chatid: str):
        assert token and chatid, (token, chatid)
        self.bot_token = token.strip()
        self.bot_chatId = chatid.strip()

    @property
    def _prefix(self):
        return f'https://api.telegram.org/bot{self.bot_token}/'

    #region CONSTRUCTORS
    @staticmethod
    def from_env(bot_token_name: str = '', chat_id_name: str = ''):
        """
        creates the object reading credentials from environment using input names

        if names are empty, uses default names
        """
        return TelegramMessager(
            read_env_var(bot_token_name or TOKEN_NAME_DEFAULT, non_empty=True),
            read_env_var(chat_id_name or CHAT_ID_NAME_DEFAULT, non_empty=True)
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
        results = requests.get(url_req)
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

        r = requests.post(send_document, data=data, files=files, stream=True)
        print(r.url)

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
            files=files
        )

        return r.json()

    def send(self, text: str = '', *files: PathLike):
        """universal function which sends text or files or both depends on existence"""
        assert text or files, 'nothing to send'

        if not files:
            return self.send_text(text)

        if len(files) == 1:
            return self.send_document(files[0], text)

        return self.send_documents(*files, caption=text)

    #endregion



