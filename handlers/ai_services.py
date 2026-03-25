import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Database
from keyboards.main_kb import get_ai_menu, get_back_button, get_upsell_keyboard
from services.ai_service import generate_response
from services.subscription import can_make_request
from config import FREE_DAILY_REQUESTS

router = Router()
logger = logging.getLogger(__name__)


class AIState(StatesGroup):
    waiting = State()


# ─── Nexus Service Map ────────────────────────────────────────────────────────
# (service_type, prompt_text, requires_premium)
SERVICE_MAP = {
    # M1 — Audience & Strategy
    "nexus_jtbd":          ("jtbd",           "🎯 Опиши продукт, нишу или бизнес-идею для JTBD-анализа:", False),
    "nexus_competitors":   ("competitors",    "🔍 Опиши свой бизнес и укажи 2-3 конкурентов (или нишу):", True),
    "nexus_plan":          ("marketing_plan", "📐 Опиши продукт, цель и бюджет для маркетингового плана:", True),
    # M2 — High-Conversion Copywriting
    "nexus_cold_copy":     ("cold_copy",      "🎯 Опиши продукт/услугу для рекламного текста (холодный трафик):", True),
    "nexus_smm_post":      ("smm_post",       "✍️ Тема или продукт для SMM-поста (AIDA, вирусный формат):", False),
    "nexus_email":         ("email_copy",     "📧 Опиши задачу письма, продукт и целевой сегмент:", True),
    "nexus_landing":       ("landing_copy",   "🖥 Опиши продукт/услугу для текста лендинга:", True),
    # M3 — Short-Form Video Scripts
    "nexus_reels":         ("reels_script",   "🎬 Тема для сценария Reels/TikTok (15-30 сек):", True),
    "nexus_shorts":        ("shorts_script",  "▶️ Тема для сценария YouTube Shorts (до 60 сек):", True),
    # M4 — Visual Asset Generation
    "nexus_creative":      ("creative_brief", "🎨 Опиши идею или продукт для Creative Brief + Midjourney промптов:", True),
    "nexus_banner":        ("ad_banner",      "🖼 Опиши продукт и платформу для концепции рекламного баннера:", True),
}

UPSELL_MSG = """🔒 <b>Это Nexus Pro-инструмент</b>

Доступен в тарифах <b>Pro</b> и <b>VIP</b>.

<b>Что разблокируешь:</b>
✅ M1: Конкурентный анализ (SWOT + 3C) и маркетинговые планы
✅ M2: Таргет-копирайтинг (PAS/BAB), email-рассылки, лендинги
✅ M3: Скрипты Reels, TikTok, YouTube Shorts
✅ M4: Creative Briefs + Midjourney промпты

💎 Pro — <b>500 ⭐/месяц</b>
👑 VIP — <b>1200 ⭐/месяц</b>

<i>1 заказ от клиента окупает подписку × 10. 🚀</i>"""

LIMIT_MSG = """⏰ <b>Дневной лимит исчерпан</b>

Использовано все <b>3 бесплатных</b> запроса сегодня.

<b>Решение:</b>
💎 <b>Pro</b> — безлимит за 500 ⭐/мес
👑 <b>VIP</b> — безлимит + приоритет за 1200 ⭐/мес

<b>Или</b> подождите до завтра 🌙
<i>Лимит сбрасывается в полночь по UTC</i>"""


def progress_bar(current: int, total: int, length: int = 10) -> str:
    filled = int(current / total * length)
    return "█" * filled + "░" * (length - filled)


@router.callback_query(F.data == "noop")
async def on_noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "ai_menu")
async def on_ai_menu(callback: CallbackQuery, db_user: dict):
    sub = db_user.get("subscription", "free") if db_user else "free"
    requests = db_user.get("daily_requests", 0) if db_user else 0

    if sub == "free":
        bar = progress_bar(requests, FREE_DAILY_REQUESTS)
        status = f"📊 Лимит: {bar} {requests}/{FREE_DAILY_REQUESTS}"
    else:
        status = f"✅ Безлимитный доступ ({sub.upper()})"

    text = f"""⚡ <b>Nexus — Инструменты</b>

{status}
━━━━━━━━━━━━━━━━━━
🆓 <b>Бесплатно:</b> JTBD-анализ, SMM-пост
🔒 <b>Pro/VIP:</b> Конкуренты, Планы, Таргет, Email, Лендинг, Reels, Shorts, Midjourney

👇 Выбери модуль:"""
    await callback.message.edit_text(text, reply_markup=get_ai_menu(sub))
    await callback.answer()


@router.callback_query(F.data.in_(SERVICE_MAP.keys()))
async def on_service_selected(callback: CallbackQuery, state: FSMContext, db_user: dict):
    if not db_user:
        await callback.answer("Сначала /start", show_alert=True)
        return

    service_key = callback.data
    service_type, prompt, requires_premium = SERVICE_MAP[service_key]
    sub = db_user.get("subscription", "free")

    if requires_premium and sub == "free":
        trial_left = db_user.get("trial_requests", 0)
        if trial_left <= 0:
            await callback.message.edit_text(UPSELL_MSG, reply_markup=get_upsell_keyboard())
            await callback.answer()
            return

    if not can_make_request(db_user):
        await callback.message.edit_text(LIMIT_MSG, reply_markup=get_upsell_keyboard())
        await callback.answer()
        return

    await state.set_state(AIState.waiting)
    await state.update_data(service_type=service_type, service_key=service_key, requires_premium=requires_premium)
    await callback.message.edit_text(
        f"{prompt}\n\n<i>Напишите текст ниже 👇</i>",
        reply_markup=get_back_button("ai_menu")
    )
    await callback.answer()


@router.message(AIState.waiting)
async def on_user_input(message: Message, state: FSMContext, db: Database, db_user: dict):
    if not db_user:
        await state.clear()
        return

    data = await state.get_data()
    service_type = data.get("service_type", "smm_post")
    requires_premium = data.get("requires_premium", False)
    sub = db_user.get("subscription", "free")

    used_trial = False
    if requires_premium and sub == "free":
        trial_left = db_user.get("trial_requests", 0)
        if trial_left > 0:
            await db.update_user(message.from_user.id, trial_requests=trial_left - 1)
            used_trial = True
        else:
            await message.answer(UPSELL_MSG, reply_markup=get_upsell_keyboard())
            await state.clear()
            return

    if not can_make_request(db_user):
        await message.answer(LIMIT_MSG, reply_markup=get_upsell_keyboard())
        await state.clear()
        return

    thinking = await message.answer("⏳ <i>Nexus генерирует стратегию... Подождите.</i>")
    response = await generate_response(service_type, message.text)

    new_count = db_user.get("daily_requests", 0) + 1
    total_ever = db_user.get("total_requests_ever", 0) + 1
    await db.update_user(message.from_user.id, daily_requests=new_count, total_requests_ever=total_ever)

    await thinking.delete()

    suffix = ""
    if used_trial:
        suffix = "\n\n<i>🎁 Использован пробный Pro-запрос. Хотите больше? /start → 💎 Подписка</i>"

    if response and len(response) > 3800:
        chunks = [response[i:i+3800] for i in range(0, len(response), 3800)]
        for i, chunk in enumerate(chunks):
            kb = get_back_button("ai_menu") if i == len(chunks) - 1 else None
            await message.answer(chunk + (suffix if i == len(chunks) - 1 else ""), reply_markup=kb)
    else:
        await message.answer((response or "❌ Нет ответа") + suffix, reply_markup=get_back_button("ai_menu"))

    await state.clear()
