# telegram-messager


Simplest util to send messages to Telegram.

## Usage

### Python

```python
from telegram_messager import TelegramMessager

TM = TelegramMessager(token='token', chatid='chatid')
TM.send_text('message')
```

### CLI

```shell
$ tgmg -h 

usage: tgmg [-h] [--text TEXT] [--files FILES [FILES ...]] [--token TOKEN] [--token-file TOKEN_FILE]
            [--token-env-var TOKEN_ENV_VAR] [--chat CHAT] [--chat-file CHAT_FILE] [--chat-env-var CHAT_ENV_VAR]

Simplest tool to send messages using Telegram HTTP API

optional arguments:
  -h, --help            show this help message and exit
  --text TEXT, -s TEXT  text to send (default: )
  --files FILES [FILES ...], -f FILES [FILES ...]
                        documents to send (default: None)
  --token TOKEN, -t TOKEN
                        bot token (default: None)
  --token-file TOKEN_FILE
                        bot token file to read token from; will be used if no --token specified (default: None)
  --token-env-var TOKEN_ENV_VAR
                        bot token environment variable name to read from; will be used if neither --token nor --token-file
                        specified (default: TELEGRAM_MESSAGER_BOT_TOKEN)
  --chat CHAT, -c CHAT  chat id (default: None)
  --chat-file CHAT_FILE
                        chat id file to read the value from (default: None)
  --chat-env-var CHAT_ENV_VAR
                        chat id environment variable name to read from (default: TELEGRAM_MESSAGER_CHAR_ID)
```


## How to create bot and channel for it

1. Create a bot by BotFather, get its `TOKEN`
2. Make public channel with `@SomeChannelName`, add this bot as admin
3. Get this `ChatId` by visiting https://api.telegram.org/botTOKEN/sendMessage?chat_id=@SomeChannelName&text=123 (with replaces):
```sh
TOKEN=t
CHANNEL=c
curl "https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=${CHANNEL}&text=123" | jq '.result.chat.id'
```
4. Make channel private (if necessary)
5. Now u can send messages to this channel by command `curl -s -X POST https://api.telegram.org/botTOKEN/sendMessage -d chat_id=ChatId -d text="your message"`
