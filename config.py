import os
from dotenv import load_dotenv

load_dotenv()

# Kotak Neo API Credentials
# Get these from https://www.kotakneo.com/
API_KEY = os.getenv("KOTAK_API_KEY", "your_api_key")
API_SECRET = os.getenv("KOTAK_API_SECRET", "your_api_secret")
MOBILE_NUMBER = os.getenv("KOTAK_MOBILE_NUMBER", "your_mobile")
PASSWORD = os.getenv("KOTAK_PASSWORD", "your_password") # or MPIN
UCC = os.getenv("KOTAK_UCC", "your_ucc")

# Application Settings
DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() == "true"
UPDATE_INTERVAL = 1 # seconds

# Trading Constants
INDICES = ["NIFTY", "BANKNIFTY"]
EXPIRY_TYPE = "WEEKLY" # or "MONTHLY"

# UI Settings
THEME_COLOR = "#1E1E1E"
POSITIVE_COLOR = "#00FF00"
NEGATIVE_COLOR = "#FF0000"
