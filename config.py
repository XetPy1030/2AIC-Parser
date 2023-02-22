# use dotenv to load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')