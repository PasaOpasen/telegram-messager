

from typing import Union
from typing_extensions import TypeAlias

import os
from pathlib import Path

import requests


PathLike: TypeAlias = Union[str, os.PathLike]


def read_text(result_path: PathLike, encoding: str = 'utf-8') -> str:
    return Path(result_path).read_text(encoding=encoding, errors='ignore')


class TelegramMessager:
    def __init__(self, token: str, chatid: str):
        self.bot_token = token
        self.bot_chatId = chatid

    @staticmethod
    def from_file(credentials_file: PathLike):
        """
        loads credentials from file with string like
            token chat_id
        """
        return TelegramMessager(*read_text(credentials_file).strip().splitlines())

    def send_document(self, path: PathLike, caption: str = ''):

        send_document = 'https://api.telegram.org/bot' + self.bot_token + '/sendDocument?'
        data = {
          'chat_id': self.bot_chatId,
          'parse_mode': 'HTML',
          'caption': caption.replace('<', '').replace('>', '')[:1024]
        }
        # Need to pass the document field in the files dict
        files = {
            'document': open(path, 'rb')
        }

        r = requests.post(send_document, data=data, files=files, stream=True)
        print(r.url)

        return r.json()

    def send_msg(self, text: str):
        url_req = (f"https://api.telegram.org/bot{self.bot_token}"
                   f"/sendMessage?chat_id={self.bot_chatId}&text={text[:1024]}")
        results = requests.get(url_req)
        return results.json()



