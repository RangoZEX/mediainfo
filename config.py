import os
import logging
from os import getenv, environ
from dotenv import load_dotenv
 
if os.path.exists('config.env'):
    load_dotenv('config.env')
    
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
class Config(object):
    BOT_TOKEN = str(os.getenv('BOT_TOKEN', '1280510378:AAGY2MT44MjWKKUErTKIOfXPPKm33dntjkk'))
    API_HASH = str(os.getenv('API_HASH', 'd02a52f4098d0d20b1be409818ec236f'))
    API_ID = int(os.getenv('API_ID', '4216648'))
    OWNER_ID = [int(x) for x in os.getenv("OWNER_ID", "1196263968").split()]

# Update globals with the variables from Config class
globals().update({key: value for key, value in vars(Config).items() if not key.startswith('__')})
