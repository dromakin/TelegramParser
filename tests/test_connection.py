from telethon import TelegramClient

# Remember to use your own values from my.telegram.org!
api_id = 1266677
api_hash = '53cd97b9eec79f46c7b0d502f9bdf6dc'
client = TelegramClient('Dmitriy_Pobeditel', api_id, api_hash)

async def main():
    # Getting information about yourself
    me = await client.get_me()

    # "me" is an User object. You can pretty-print
    # any Telegram object with the "stringify" method:
    print(me.stringify())

    # When you print something, you see a representation of it.
    # You can access all attributes of Telegram objects with
    # the dot operator. For example, to get the username:
    username = me.username
    print(username)
    print(me.phone)


with client:
    client.loop.run_until_complete(main())


