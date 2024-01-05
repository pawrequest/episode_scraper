import os

DEBUG = os.environ.get("DEBUG", False)
SLEEP = os.environ.get("SLEEP", 600)
MAIN_URL = os.environ.get("MAIN_URL", None)
MAX_DUPES = os.environ.get("MAX_DUPES", 3)
if MAIN_URL is None:
    raise ValueError("MAIN_URL environment variable not set")
