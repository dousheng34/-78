import json
import base64
import logging
import hashlib
import aiohttp
from datetime import datetime, date
from typing import Optional, Dict, Any
from config import GITHUB_TOKEN, GITHUB_REPO

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.data: Dict[str, Any] = {
            "users": {},
            "transactions": [],
            "stats": {"total_users": 0, "total_revenue_stars": 0, "total_transactions": 0}
        }
        self._file_sha: Optional[str] = None
        self._db_path = "database.json"

    async def load(self):
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{self._db_path}"
                headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self._file_sha = data.get("sha")
                        content = base64.b64decode(data["content"]).decode("utf-8")
                        self.data = json.loads(content)
                        logger.info("Database loaded from GitHub")
                    elif resp.status == 404:
                        logger.info("DB not found, creating...")
                        await self.save()
                    else:
                        logger.error(f"Failed to load DB: {resp.status}")
        except Exception as e:
            logger.error(f"Error loading DB: {e}")

    async def save(self):
        try:
            content = json.dumps(self.data, ensure_ascii=False, indent=2, default=str)
            encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            async with aiohttp.ClientSession() as session:
                url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{self._db_path}"
                headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
                payload = {
                    "message": f"Update DB {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "content": encoded
                }
                if self._file_sha:
                    payload["sha"] = self._file_sha
                async with session.put(url, headers=headers, json=payload) as resp:
                    if resp.status in (200, 201):
                        result = await resp.json()
                        self._file_sha = result["content"]["sha"]
                    else:
                        text = await resp.text()
                        logger.error(f"Failed to save DB: {resp.status} - {text}")
        except Exception as e:
            logger.error(f"Error saving DB: {e}")

    def get_user(self, user_id: int) -> Optional[Dict]:
        return self.data["users"].get(str(user_id))

    async def create_user(self, user_id: int, username: str, first_name: str,
                          referral_code: str, referred_by: Optional[str] = None):
        user_data = {
            "id": user_id,
            "username": username or "",
            "first_name": first_name or "Пользователь",
            "subscription": "free",
            "subscription_end": None,
            "daily_requests": 0,
            "last_request_date": str(date.today()),
            "referral_code": referral_code,
            "referred_by": referred_by,
            "total_referrals": 0,
            "stars_balance": 0,
            "pending_service": None,
            "joined_at": datetime.now().isoformat()
        }
        self.data["users"][str(user_id)] = user_data
        self.data["stats"]["total_users"] += 1
        await self.save()
        return user_data

    async def update_user(self, user_id: int, **kwargs):
        if str(user_id) in self.data["users"]:
            self.data["users"][str(user_id)].update(kwargs)
            await self.save()

    async def add_transaction(self, user_id: int, amount: int, service: str, payload: str):
        transaction = {
            "id": len(self.data["transactions"]) + 1,
            "user_id": user_id,
            "amount": amount,
            "service": service,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }
        self.data["transactions"].append(transaction)
        self.data["stats"]["total_revenue_stars"] += amount
        self.data["stats"]["total_transactions"] += 1
        await self.save()
        return transaction

    def get_stats(self) -> Dict:
        return self.data["stats"]

    def get_all_users(self) -> Dict:
        return self.data["users"]

    def get_transactions(self, limit: int = 10) -> list:
        return self.data["transactions"][-limit:]

    def reset_daily_requests_if_needed(self, user: Dict) -> bool:
        today = str(date.today())
        if user.get("last_request_date") != today:
            user["daily_requests"] = 0
            user["last_request_date"] = today
            return True
        return False

    def generate_referral_code(self, user_id: int) -> str:
        return hashlib.md5(f"{user_id}_bot_secret_2024".encode()).hexdigest()[:8].upper()
