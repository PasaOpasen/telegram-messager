# telegram-messager


Simplest util to send messages to Telegram.

Usage:
```python
from telegram_messager import TelegramMessager

TM = TelegramMessager(token='token', chatid='chatid')
TM.send_msg('message')
```


## How to create bot and channel for it

1. Create a bot by BotFather, get its `TOKEN`
2. Make public channel with `@SomeChannelName`, add this bot as admin
3. Get this `ChatId` by visiting https://api.telegram.org/botTOKEN/sendMessage?chat_id=@SomeChannelName&text=123 (with replaces)
4. Make channel private (if necessary)
5. Now u can send messages to this channel by command `curl -s -X POST https://api.telegram.org/botTOKEN/sendMessage -d chat_id=ChatId -d text="your message"`
