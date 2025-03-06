import os
import logging

HOSTNAME = os.environ.get("HOSTNAME")
USERNAME = os.environ.get("USER_ID")
PASSWORD = os.environ.get("PASSWORD")
DATABASE = os.environ.get("DATABASE")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_MAXIMUM_REQUESTS = os.environ.get("GOOGLE_MAXIMUM_REQUESTS", 200)
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/indexing",
    "https://www.googleapis.com/auth/webmasters"
]

BING_MAXIMUM_REQUESTS = 10000
BING_MAXIMUM_SIZE = 500

LOGGING_LEVEL = logging.INFO
LOGGING_DATEFORMAT = "%Y-%m-%dT%H:%M:%S"
LOGGING_FORMAT = '[%(levelname)s] %(asctime)s: %(message)s'
logging.basicConfig(
    level=LOGGING_LEVEL,
    datefmt=LOGGING_DATEFORMAT,
    format=LOGGING_FORMAT
)
