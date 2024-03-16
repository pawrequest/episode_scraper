import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get("DEBUG", False)
SLEEP = os.environ.get("SLEEP", 600)
MAIN_URL = os.environ.get("MAIN_URL", None)
MAX_DUPES = os.environ.get("MAX_DUPES", 3)
HTML_TITLE = os.environ.get("HTML_TITLE", "")
