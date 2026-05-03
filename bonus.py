from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta
import random
from utils.keyboards import back_kb
from utils.texts import t
from utils import db

router = Router()

@router.callback_query(F.data == "bonus")
async def daily_bonus(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db.get_bot_lang()
    
    last_bonus = db.get_last_bonus(user_id)
    
    if last_bonus:
        last_dt = datetime.fromisoformat(last_bonus)
        now = datetime.now()
        diff = now - last_dt
        
        if diff.total_seconds() < 86400:  # 24 hours
            remaining = timedelta(seconds=86400) - diff
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            
            await callback.message.edit_text(
                t("bonus_already", lang, time=f"{hours}s {minutes}d"),
                reply_markup=back_kb(),
                parse_mode="HTML"
            )
            await callback.answer("⏳ Bonus allaqachon olindi!")
            return
    
    # Give bonus
    points = random.randint(10, 100)
    db.add_user_score(user_id, points)
    db.set_last_bonus(user_id)
    total = db.get_user_score(user_id)
    
    await callback.message.edit_text(
        t("bonus_received", lang, points=points, total=total),
        reply_markup=back_kb(),
        parse_mode="HTML"
    )
    await callback.answer(f"🎁 +{points} ball!")
