import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

WIT_TOKEN = os.environ.get("WIT_TOKEN")
BOT_SLACK_NAME = os.environ.get("BOT_SLACK_NAME")
BOT_SLACK_TOKEN = os.environ.get("BOT_SLACK_TOKEN")
BOT_SLACK_ID = os.environ.get("BOT_SLACK_ID")
SLACK_API = os.environ.get("SLACK_API")
SLACK_VERIFY_TOKEN = os.environ.get("SLACK_VERIFY")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
WIT_TOKEN = os.environ.get("WIT_TOKEN")