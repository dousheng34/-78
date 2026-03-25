import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from database import Database
from keyboards.main_kb import get_main_menu, get_back_button
from services.subscription import get_subscription_info
from services.referral_service import process_referral

router = Router()
logger = logging.getLogger(__name__)

WELCOME = """🧠 <b>Привет, {name}!</b>

Я <b>Nexus</b> — автономный ИИ-архитектор перфоманс-маркетинга.

━━━━━━━━━━━━━━━━━━
<b>4 профессиональных модуля:</b>
🎯 M1 — Аудитория и стратегия (JTBD, конкуренты)
✍️ M2 — Копирайтинг (PAS, AIDA, QUEST, лендинги)
🎬 M3 — Сценарии Reels, TikTok, YouTube Shorts
🎨 M4 — Visual Brief + Midjourney промпты
━━━━━━━━━━━━━━━━━━

<b>📊 Тариф:</b> {plan}
<b>💡 Запросов сегодня:</b> {requests}

{trial_msg}

👇 <i>Выбери модуль:</i>"""

TRIAL_NEW = "🎁 <b>Подарок:</b> 1 бесплатный Pro-запрос активирован!"
TRIAL_NONE = "⚡ <i>Бесплатно: 3 запроса/день | Pro/VIP: безлимит</i>"


def get_plan_label(user: dict) -> str:
    sub = user.get("subscription", "free")
    labels = {"free": "🆓 Бесплатный", "pro": "💎 Pro", "vip": "👑 VIP"}
    return labels.get(sub, "🆓 Бесплатный")


@router.message(CommandStart())
async def cmd_start(message: Message, db: Database, db_user: dict):
    user = message.from_user
    is_new = db_user is None

    if is_new:
        referral_code = db.generate_referral_code(user.id)
        referred_by = None
        args = message.text.split()
        if len(args) > 1:
            referrer = await process_referral(db, user.id, args[1])
            if referrer:
                referred_by = args[1]
        db_user = await db.create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            referral_code=referral_code,
            referred_by=referred_by
        )
        await db.update_user(user.id, trial_requests=1)
        trial_msg = TRIAL_NEW
    else:
        trial_msg = TRIAL_NONE

    requests_today = db_user.get("daily_requests", 0)
    limit = "∞" if db_user.get("subscription", "free") != "free" else f"{requests_today}/3"

    text = WELCOME.format(
        name=user.first_name,
        plan=get_plan_label(db_user),
        requests=limit,
        trial_msg=trial_msg
    )
    await message.answer(text, reply_markup=get_main_menu(db_user.get("subscription", "free")))


@router.callback_query(F.data == "main_menu")
async def on_main_menu(callback: CallbackQuery, db_user: dict):
    user = callback.from_user
    sub = db_user.get("subscription", "free") if db_user else "free"
    requests_today = db_user.get("daily_requests", 0) if db_user else 0
    limit = "∞" if sub != "free" else f"{requests_today}/3"
    text = WELCOME.format(
        name=user.first_name,
        plan=get_plan_label(db_user) if db_user else "🆓 Бесплатный",
        requests=limit,
        trial_msg=TRIAL_NONE
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu(sub))
    await callback.answer()


@router.callback_query(F.data == "profile")
async def on_profile(callback: CallbackQuery, db_user: dict):
    if not db_user:
        await callback.answer("Сначала /start", show_alert=True)
        return
    sub = db_user.get("subscription", "free")
    earned_stars = db_user.get("stars_balance", 0)
    refs = db_user.get("total_referrals", 0)
    requests = db_user.get("daily_requests", 0)
    joined = db_user.get("joined_at", "")[:10]

    badges = []
    if db_user.get("total_requests_ever", 0) >= 1:
        badges.append("🌟")
    if refs >= 1:
        badges.append("👥")
    if refs >= 5:
        badges.append("🏆")
    if sub == "pro":
        badges.append("💎")
    if sub == "vip":
        badges.append("👑")
    badge_str = " ".join(badges) if badges else "—"

    plan_labels = {
        "free": "🆓 Бесплатный (3 запроса/день)",
        "pro": "💎 Pro (безлимит)",
        "vip": "👑 VIP (безлимит + приоритет)"
    }

    text = f"""👤 <b>Профиль — Nexus</b>

━━━━━━━━━━━━━━━━━━
🆔 ID: <code>{db_user['id']}</code>
📅 С нами с: {joined}
🎖 Достижения: {badge_str}

<b>📊 Подписка:</b>
{plan_labels.get(sub, "🆓 Бесплатный")}

<b>📈 Статистика:</b>
• Запросов сегодня: {requests}
• Рефералов: {refs} чел.
• Stars накоплено: {earned_stars} ⭐
━━━━━━━━━━━━━━━━━━"""
    await callback.message.edit_text(text, reply_markup=get_back_button())
    await callback.answer()


@router.callback_query(F.data == "achievements")
async def on_achievements(callback: CallbackQuery, db_user: dict):
    if not db_user:
        await callback.answer("Сначала /start", show_alert=True)
        return
    sub = db_user.get("subscription", "free")
    refs = db_user.get("total_referrals", 0)
    total_reqs = db_user.get("total_requests_ever", 0)

    def check(condition, icon, name, desc):
        status = "✅" if condition else "⬜"
        return f"{status} {icon} <b>{name}</b>\n   <i>{desc}</i>"

    lines = [
        check(total_reqs >= 1,  "🌟", "Первый инсайт",   "Выполни первый Nexus-запрос"),
        check(total_reqs >= 5,  "🔥", "В потоке",         "5 запросов выполнено"),
        check(total_reqs >= 50, "⚡", "Перфоманс-мастер", "50 запросов выполнено"),
        check(refs >= 1,        "👥", "Коннектор",        "Пригласи первого маркетолога"),
        check(refs >= 5,        "🏆", "Нетворкер",        "5 рефералов → бесплатный Pro!"),
        check(sub in ("pro", "vip"), "💎", "Pro-стратег", "Оформи подписку Pro"),
        check(sub == "vip",     "👑", "CMO-уровень",      "Оформи подписку VIP"),
    ]
    completed = sum(1 for l in lines if l.startswith("✅"))
    text = f"""🏆 <b>Достижения Nexus</b>

Выполнено: {completed}/{len(lines)}
{"█" * completed}{"░" * (len(lines) - completed)}

{chr(10).join(lines)}

<i>💡 Достижения открывают бонусы и статус!</i>"""
    await callback.message.edit_text(text, reply_markup=get_back_button())
    await callback.answer()


@router.callback_query(F.data == "help")
async def on_help(callback: CallbackQuery):
    text = """❓ <b>Справка — Nexus</b>

<b>🚀 Как работать:</b>
1. Нажми «⚡ Nexus Инструменты»
2. Выбери нужный модуль (M1–M4)
3. Опиши задачу → получи экспертный результат

<b>📊 Тарифы:</b>
🆓 <b>Free</b> — JTBD-анализ + SMM-пост, 3 запроса/день
💎 <b>Pro</b> — все 11 инструментов, безлимит (500 ⭐/мес)
👑 <b>VIP</b> — Pro + приоритет обработки (1200 ⭐/мес)

<b>👥 Реферальная программа:</b>
• +10 Stars за каждого приглашённого
• 5 рефералов = 1 месяц Pro бесплатно!

<b>💡 Принцип Nexus:</b> Никакой воды. Только Data-Driven стратегии и конверсионные тексты. 🎯"""
    await callback.message.edit_text(text, reply_markup=get_back_button())
    await callback.answer()
