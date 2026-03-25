from datetime import datetime, timedelta
from typing import Dict

SUBSCRIPTION_TIERS = {
    "free":  {"name": "🆓 Бесплатный", "daily_requests": 3},
    "pro":   {"name": "💎 Pro",         "daily_requests": -1},
    "vip":   {"name": "👑 VIP",         "daily_requests": -1},
}


def is_subscription_active(user: Dict) -> bool:
    if user["subscription"] == "free":
        return True
    end = user.get("subscription_end")
    if not end:
        return False
    return datetime.now() < datetime.fromisoformat(end)


def can_make_request(user: Dict) -> bool:
    if not is_subscription_active(user):
        return False
    tier = user["subscription"]
    if SUBSCRIPTION_TIERS[tier]["daily_requests"] == -1:
        return True
    return user.get("daily_requests", 0) < SUBSCRIPTION_TIERS["free"]["daily_requests"]


def get_subscription_info(user: Dict) -> str:
    tier = user["subscription"]
    name = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["free"])["name"]
    if tier == "free":
        return f"Тариф: {name}\nЗапросов сегодня: {user.get('daily_requests', 0)}/3"
    end = user.get("subscription_end")
    if end:
        end_dt = datetime.fromisoformat(end)
        days = (end_dt - datetime.now()).days
        return f"Тариф: {name}\nАктивна до: {end_dt.strftime('%d.%m.%Y')} ({days} дн.)"
    return f"Тариф: {name}"


def get_subscription_end_date(months: int = 1) -> str:
    return (datetime.now() + timedelta(days=30 * months)).isoformat()
