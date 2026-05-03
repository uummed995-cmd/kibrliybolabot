import asyncio
import logging
from datetime import datetime, timedelta
from utils import db

logger = logging.getLogger(__name__)

# Track quiz activity
last_quiz_time = {}
quiz_check_interval = 1800  # 30 minutes

async def start_scheduler(bot):
    asyncio.create_task(quiz_monitor_task(bot))
    asyncio.create_task(daily_reminder_task(bot))
    logger.info("✅ Scheduler tasks started")

async def quiz_monitor_task(bot):
    """Check if quiz is active in group every 30 minutes"""
    await asyncio.sleep(60)  # Initial delay
    while True:
        try:
            group_id = db.get_group_id()
            if group_id:
                last = db.get_setting("last_quiz_time")
                if last:
                    last_dt = datetime.fromisoformat(last)
                    diff = (datetime.now() - last_dt).total_seconds()
                    # If no quiz for 2 hours, alert admins
                    if diff > 7200:
                        await alert_admins_quiz(bot, group_id)
        except Exception as e:
            logger.error(f"Quiz monitor error: {e}")
        await asyncio.sleep(quiz_check_interval)

async def daily_reminder_task(bot):
    """Send daily reminder at 9 AM"""
    while True:
        try:
            now = datetime.now()
            next_9am = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now >= next_9am:
                next_9am += timedelta(days=1)
            wait = (next_9am - now).total_seconds()
            await asyncio.sleep(wait)
            group_id = db.get_group_id()
            if group_id:
                try:
                    await bot.send_message(
                        group_id,
                        "☀️ <b>Yangi kun boshlandi!</b>\n\n"
                        "🎯 Bugun ham ingliz tilini o'rganishda davom eting!\n"
                        "💬 Guruhda faol bo'ling va test yechishni unutmang!\n\n"
                        "🎁 Botdagi kunlik bonusni ham olishni unutmang!",
                        parse_mode="HTML"
                    )
                except:
                    pass
        except Exception as e:
            logger.error(f"Daily reminder error: {e}")
        await asyncio.sleep(86400)

async def alert_admins_quiz(bot, group_id):
    """Alert all admins that quiz is not active"""
    from utils.texts import t
    try:
        admins = await bot.get_chat_administrators(group_id)
        mentions = ""
        for admin in admins:
            if not admin.user.is_bot:
                mentions += f'<a href="tg://user?id={admin.user.id}">{admin.user.first_name}</a> '
        
        if mentions:
            text = t("no_quiz_long") + f"\n\n{mentions}"
            await bot.send_message(group_id, text, parse_mode="HTML")
            db.set_setting("last_quiz_time", datetime.now().isoformat())
    except Exception as e:
        logger.error(f"Alert admins error: {e}")

def update_quiz_time():
    db.set_setting("last_quiz_time", datetime.now().isoformat())
