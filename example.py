
from telegram_messager import TelegramMessager

TM = TelegramMessager(token='token', chatid='chatid')
TM.send_text('message')


TM = TelegramMessager.from_file('./creds.txt')
TM.send_document('version.txt', caption='caption')

TM.send_documents('version.txt', 'setup.py', 'Makefile', caption='text')

TM.send('text', 'setup.py', 'Makefile')
