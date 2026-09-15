import os
from dotenv import load_dotenv

load_dotenv()

from backend.starter import AppStarter

starter = AppStarter()
app = starter.get_app()
