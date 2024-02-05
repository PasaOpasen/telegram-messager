

from typing import Union
from typing_extensions import TypeAlias

import os
from pathlib import Path

import json
import requests


PathLike: TypeAlias = Union[str, os.PathLike]


def read_text(result_path: PathLike, encoding: str = 'utf-8') -> str:
    """reads file text"""
    return Path(result_path).read_text(encoding=encoding, errors='ignore')


def _preprocess_text(text: str) -> str:
    t = text.replace('<', '').replace('>', '')
    if len(t) >= 1024:
        return t[:1021] + '...'
    return t


class TelegramMessager:
    def __init__(self, token: str, chatid: str):
        self.bot_token = token
        self.bot_chatId = chatid

    @property
    def _prefix(self):
        return f'https://api.telegram.org/bot{self.bot_token}/'

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

    def send_msg(self, text: str):
        url_req = (self._prefix +
                   f"sendMessage?chat_id={self.bot_chatId}&text={_preprocess_text(text)}")
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





