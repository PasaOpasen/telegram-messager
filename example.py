
from telegram_messager import TelegramMessager

TM = TelegramMessager(token='token', chatid='chatid')
TM.send_msg('message')


TM = TelegramMessager.from_file('./creds.txt')
TM.send_document('version.txt', caption='caption')

TM.send_documents('version.txt', 'setup.py', 'Makefile', caption='text')


