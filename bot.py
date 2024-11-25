import logging
import logging.config

# Set up logging
logging.config.fileConfig('logging.conf')  # Ensure you have the logging.conf file
logging.getLogger().setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import API_ID, API_HASH, BOT_TOKEN
import pyromod.listen  # This is likely for any custom extensions or listeners

class Bot(Client):
    def __init__(self):
        super().__init__(
            "MediaInfoXBot",
            api_id=API_ID, 
            api_hash=API_HASH, 
            bot_token=BOT_TOKEN, 
            workers=50,  # Number of concurrent workers
            plugins={"root": "plugins"}  # Load plugins from the "plugins" folder
        )

    async def start(self):
        try:
            await super().start()
            me = await self.get_me()  # Get bot's information
            self.username = '@' + me.username
            print(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        except Exception as e:
            logging.error(f"Error starting bot: {str(e)}")
            print(f"Error starting bot: {str(e)}")

    async def stop(self, *args):
        try:
            await super().stop()  # Stop the bot
            print("Bot stopped. Bye.")
        except Exception as e:
            logging.error(f"Error stopping bot: {str(e)}")
            print(f"Error stopping bot: {str(e)}")


if __name__ == "__main__":
    app = Bot()
    try:
        app.run()  # Run the bot
    except Exception as e:
        logging.error(f"Error running bot: {str(e)}")
        print(f"Error running bot: {str(e)}")
