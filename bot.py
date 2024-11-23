import logging
import logging.config
 
# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.ERROR)
 
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from plugins import Media
from config import API_ID, API_HASH, BOT_TOKEN
import pyromod.listen
 
class Bot(Client):
 
    def __init__(self):
        super().__init__(
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "Fonts"}
        )
 
    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username
        print(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
 
    async def stop(self, *args):
        await super().stop()
        print("Bot stopped. Bye.")
 
 
app = Bot()
app.run()
