import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8731918527:AAH7qe33czifsRU_fpRm5BYtHLb_AjRQudg")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6476337043"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "@kibrliybolabot")

# Default settings
DEFAULT_LANG = "uz"
WARN_LIMIT = 3
MUTE_DURATION = 10  # minutes
SPAM_THRESHOLD = 5  # messages per 10 seconds
SPAM_WINDOW = 10    # seconds

# Database file
DB_FILE = "data/bot_data.json"
