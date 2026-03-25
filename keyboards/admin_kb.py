from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
    )
    b.row(
        InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="💰 Транзакции", callback_data="admin_transactions"),
    )
    b.row(InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu"))
    return b.as_markup()
