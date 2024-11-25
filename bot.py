import logging
import logging.config
import sys
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import API_ID, API_HASH, BOT_TOKEN
import pyromod.listen

# Set up logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger("bot")

class Bot(Client):
    def __init__(self):
        super().__init__(
            "MediaInfoXBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"}
        )

    async def start(self):
        try:
            await super().start()
            me = await self.get_me()
            self.username = '@' + me.username
            logger.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started as {me.username}.")
            print(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}", exc_info=True)
            print(f"Error starting bot: {str(e)}")

    async def stop(self, *args):
        try:
            await super().stop()
            logger.info("Bot stopped successfully.")
            print("Bot stopped. Bye.")
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}", exc_info=True)
            print(f"Error stopping bot: {str(e)}")

if __name__ == "__main__":
    app = Bot()
    try:
        app.run()
    except Exception as e:
        logger.critical(f"Error running bot: {str(e)}", exc_info=True)
        print(f"Error running bot: {str(e)}")
        
