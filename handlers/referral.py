import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import Database
from keyboards.main_kb import get_back_button
from config import REFERRAL_BONUS_STARS, REFERRAL_PRO_THRESHOLD

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "referral_menu")
async def on_referral_menu(callback: CallbackQuery, db: Database, db_user: dict):
    if not db_user:
        await callback.answer("Сначала нажмите /start", show_alert=True)
        return

    ref_code = db_user.get("referral_code", "N/A")
    total = db_user.get("total_referrals", 0)
    stars = db_user.get("stars_balance", 0)
    need = max(0, REFERRAL_PRO_THRESHOLD - total)
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={ref_code}"

    bar = "█" * total + "░" * max(0, REFERRAL_PRO_THRESHOLD - total)

    text = f"""👥 <b>Реферальная программа Nexus</b>

🔗 <b>Ваша ссылка:</b>
<code>{ref_link}</code>

📊 <b>Прогресс к бесплатному Pro:</b>
{bar} {total}/{REFERRAL_PRO_THRESHOLD}

<b>Статистика:</b>
• Приглашено: {total} маркетолог(ов)
• Заработано: {stars} ⭐

🎁 <b>Бонусы:</b>
• +{REFERRAL_BONUS_STARS} Stars за каждого друга
• Ещё {need} чел. → 1 месяц Pro бесплатно!

<i>Делитесь ссылкой с маркетологами, SMM-специалистами и владельцами бизнеса.</i>"""

    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(
        text="📤 Поделиться ссылкой",
        url=f"https://t.me/share/url?url={ref_link}&text=Попробуй Nexus — AI-архитектор маркетинга. Стратегии, копирайтинг, скрипты Reels и Midjourney промпты в одном боте!"
    ))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    await callback.message.edit_text(text, reply_markup=b.as_markup())
    await callback.answer()
