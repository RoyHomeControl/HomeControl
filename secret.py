from dotenv import load_dotenv
import os

load_dotenv()

COUCH_USER = os.getenv("COUCH_USER")
COUCH_PASSWORD = os.getenv("COUCH_PASSWORD")