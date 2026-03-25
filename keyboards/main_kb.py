from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu(subscription: str = "free") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⚡ Nexus Инструменты", callback_data="ai_menu"))
    b.row(
        InlineKeyboardButton(
            text="💎 Подписка" + (" ✓" if subscription != "free" else ""),
            callback_data="premium_menu"
        ),
        InlineKeyboardButton(text="👥 Рефералы", callback_data="referral_menu"),
    )
    b.row(
        InlineKeyboardButton(text="📊 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements"),
    )
    b.row(InlineKeyboardButton(text="❓ Помощь", callback_data="help"))
    return b.as_markup()


def get_ai_menu(subscription: str = "free") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    lock = "" if subscription != "free" else " 🔒"

    # M1 — Audience & Strategy
    b.row(InlineKeyboardButton(text="━━ M1: Аудитория и Стратегия ━━", callback_data="noop"))
    b.row(InlineKeyboardButton(text="🎯 JTBD-анализ (бесплатно)", callback_data="nexus_jtbd"))
    b.row(
        InlineKeyboardButton(text=f"🔍 Конкуренты{lock}", callback_data="nexus_competitors"),
        InlineKeyboardButton(text=f"📐 Маркетинг-план{lock}", callback_data="nexus_plan"),
    )

    # M2 — Copywriting
    b.row(InlineKeyboardButton(text="━━ M2: Копирайтинг ━━", callback_data="noop"))
    b.row(InlineKeyboardButton(text="✍️ SMM-пост (бесплатно)", callback_data="nexus_smm_post"))
    b.row(
        InlineKeyboardButton(text=f"🎯 Таргет-текст{lock}", callback_data="nexus_cold_copy"),
        InlineKeyboardButton(text=f"📧 Email-рассылка{lock}", callback_data="nexus_email"),
    )
    b.row(InlineKeyboardButton(text=f"🖥 Лендинг{lock}", callback_data="nexus_landing"))

    # M3 — Short-Form Video
    b.row(InlineKeyboardButton(text="━━ M3: Short-Form Video ━━", callback_data="noop"))
    b.row(
        InlineKeyboardButton(text=f"📱 Reels/TikTok{lock}", callback_data="nexus_reels"),
        InlineKeyboardButton(text=f"▶️ YouTube Shorts{lock}", callback_data="nexus_shorts"),
    )

    # M4 — Visual Assets
    b.row(InlineKeyboardButton(text="━━ M4: Визуальные Активы ━━", callback_data="noop"))
    b.row(
        InlineKeyboardButton(text=f"🎨 Creative Brief{lock}", callback_data="nexus_creative"),
        InlineKeyboardButton(text=f"🖼 Баннер-промпт{lock}", callback_data="nexus_banner"),
    )

    if subscription == "free":
        b.row(InlineKeyboardButton(text="🔓 Разблокировать Pro-модули", callback_data="premium_menu"))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    return b.as_markup()


def get_back_button(callback: str = "main_menu") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=callback))
    return b.as_markup()


def get_upsell_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💎 Купить Pro — 500 ⭐", callback_data="buy_pro"))
    b.row(InlineKeyboardButton(text="👑 Купить VIP — 1200 ⭐", callback_data="buy_vip"))
    b.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="ai_menu"))
    return b.as_markup()
