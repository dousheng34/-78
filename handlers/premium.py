import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice
from database import Database
from keyboards.premium_kb import get_premium_menu, get_one_time_menu, get_payment_confirm
from keyboards.main_kb import get_back_button
from services.subscription import get_subscription_info
from config import PRICE_PRO_MONTHLY, PRICE_VIP_MONTHLY, PRICE_RESUME, PRICE_BUSINESS_PLAN, PRICE_CONTENT

router = Router()
logger = logging.getLogger(__name__)

PREMIUM_TEXT = """💎 <b>Nexus — Тарифы</b>

🆓 <b>Бесплатный</b>
• JTBD-анализ + SMM-пост
• 3 запроса/день

━━━━━━━━━━━━

💎 <b>Pro — {pro} ⭐/месяц</b>
• ✅ Все 11 Nexus-инструментов
• ✅ Конкурентный анализ (SWOT + 3C)
• ✅ Таргет-копирайтинг (PAS/BAB/QUEST)
• ✅ Сценарии Reels, TikTok, Shorts
• ✅ Midjourney промпты и Creative Brief
• ✅ Безлимитные запросы 24/7

━━━━━━━━━━━━

👑 <b>VIP — {vip} ⭐/месяц</b>
• ✅ Всё из Pro
• ✅ Приоритетная обработка
• ✅ Персональные шаблоны под нишу

💫 Оплата через Telegram Stars!"""

PAYMENT_MAP = {
    "buy_pro":      ("💎 Nexus Pro (1 мес)",       PRICE_PRO_MONTHLY,   "sub_pro"),
    "buy_vip":      ("👑 Nexus VIP (1 мес)",       PRICE_VIP_MONTHLY,   "sub_vip"),
    "buy_resume":   ("📄 Разовый пакет: Резюме",   PRICE_RESUME,        "one_resume"),
    "buy_business": ("📐 Разовый пакет: Бизнес-план", PRICE_BUSINESS_PLAN, "one_business"),
    "buy_content":  ("✍️ Разовый пакет: Контент",  PRICE_CONTENT,       "one_content"),
}


@router.callback_query(F.data == "premium_menu")
async def on_premium_menu(callback: CallbackQuery, db_user: dict):
    text = PREMIUM_TEXT.format(pro=PRICE_PRO_MONTHLY, vip=PRICE_VIP_MONTHLY)
    if db_user:
        text = f"<b>Ваш тариф:</b> {get_subscription_info(db_user)}\n\n" + text
    await callback.message.edit_text(text, reply_markup=get_premium_menu())
    await callback.answer()


@router.callback_query(F.data == "one_time_purchases")
async def on_one_time(callback: CallbackQuery):
    text = f"""🛒 <b>Разовые пакеты</b>

📄 Резюме — {PRICE_RESUME} ⭐
📐 Бизнес-план — {PRICE_BUSINESS_PLAN} ⭐
✍️ Контент-пакет (5 постов) — {PRICE_CONTENT} ⭐"""
    await callback.message.edit_text(text, reply_markup=get_one_time_menu())
    await callback.answer()


@router.callback_query(F.data.in_(PAYMENT_MAP.keys()))
async def on_buy(callback: CallbackQuery):
    name, price, payload = PAYMENT_MAP[callback.data]
    text = f"🛒 <b>Подтверждение</b>\n\nТовар: <b>{name}</b>\nЦена: <b>{price} ⭐</b>\n\nStars спишутся с баланса Telegram."
    await callback.message.edit_text(text, reply_markup=get_payment_confirm(price, payload))
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_payment:"))
async def on_confirm_payment(callback: CallbackQuery):
    parts = callback.data.split(":")
    payload, price = parts[1], int(parts[2])
    payload_names = {
        "sub_pro":      "💎 Nexus Pro — 1 месяц",
        "sub_vip":      "👑 Nexus VIP — 1 месяц",
        "one_resume":   "📄 Пакет: Резюме",
        "one_business": "📐 Пакет: Бизнес-план",
        "one_content":  "✍️ Пакет: Контент (5 постов)",
    }
    title = payload_names.get(payload, "Покупка")
    await callback.message.answer_invoice(
        title=title,
        description=f"Оплата: {title}",
        payload=payload,
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=price)],
    )
    await callback.answer()
