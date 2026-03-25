import logging
from typing import Optional
from config import REFERRAL_BONUS_STARS, REFERRAL_PRO_THRESHOLD

logger = logging.getLogger(__name__)


async def process_referral(db, new_user_id: int, referral_code: str) -> Optional[int]:
    for uid, user in db.get_all_users().items():
        if user.get("referral_code") == referral_code and int(uid) != new_user_id:
            referrer_id = int(uid)
            new_total = user.get("total_referrals", 0) + 1
            updates = {
                "total_referrals": new_total,
                "stars_balance": user.get("stars_balance", 0) + REFERRAL_BONUS_STARS
            }
            if new_total >= REFERRAL_PRO_THRESHOLD:
                from services.subscription import get_subscription_end_date
                updates["subscription"] = "pro"
                updates["subscription_end"] = get_subscription_end_date(1)
                logger.info(f"User {referrer_id} got free Pro for {REFERRAL_PRO_THRESHOLD} referrals!")
            await db.update_user(referrer_id, **updates)
            logger.info(f"Referral: {new_user_id} referred by {referrer_id}")
            return referrer_id
    return None
