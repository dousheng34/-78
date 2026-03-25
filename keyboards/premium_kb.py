from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import PRICE_PRO_MONTHLY, PRICE_VIP_MONTHLY, PRICE_RESUME, PRICE_BUSINESS_PLAN, PRICE_CONTENT


def get_premium_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=f"💎 Pro — {PRICE_PRO_MONTHLY} ⭐/мес", callback_data="buy_pro"))
    b.row(InlineKeyboardButton(text=f"👑 VIP — {PRICE_VIP_MONTHLY} ⭐/мес", callback_data="buy_vip"))
    b.row(InlineKeyboardButton(text="🛒 Разовые покупки", callback_data="one_time_purchases"))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    return b.as_markup()


def get_one_time_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=f"📄 Резюме — {PRICE_RESUME} ⭐", callback_data="buy_resume"))
    b.row(InlineKeyboardButton(text=f"📋 Бизнес-план — {PRICE_BUSINESS_PLAN} ⭐", callback_data="buy_business"))
    b.row(InlineKeyboardButton(text=f"✍️ Контент-пакет — {PRICE_CONTENT} ⭐", callback_data="buy_content"))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="premium_menu"))
    return b.as_markup()


def get_payment_confirm(price: int, payload: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=f"⭐ Оплатить {price} Stars", callback_data=f"confirm_payment:{payload}:{price}"))
    b.row(InlineKeyboardButton(text="❌ Отмена", callback_data="premium_menu"))
    return b.as_markup()
