"""Configuration and environment variables"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except ValueError:
    raise ValueError("ADMIN_ID must be a valid integer")

if ADMIN_ID == 0:
    raise ValueError("ADMIN_ID environment variable is not set")

# OLT Configuration (optional)
OLT_HOST = os.getenv("OLT_HOST", "192.168.1.1")
OLT_USERNAME = os.getenv("OLT_USERNAME", "admin")
OLT_PASSWORD = os.getenv("OLT_PASSWORD", "")

# Debug mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
OLT_PORT = int(os.getenv("OLT_PORT", "23"))
