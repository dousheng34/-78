import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")
WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
PORT: int = int(os.getenv("PORT", "8000"))

# Subscription prices in Telegram Stars
PRICE_PRO_MONTHLY = 500
PRICE_VIP_MONTHLY = 1200
PRICE_RESUME = 50
PRICE_BUSINESS_PLAN = 100
PRICE_CONTENT = 30

# Free tier limits
FREE_DAILY_REQUESTS = 3

# Referral
REFERRAL_BONUS_STARS = 10
REFERRAL_PRO_THRESHOLD = 5
