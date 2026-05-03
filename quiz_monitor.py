from aiogram import Router, F
from aiogram.types import Message
from utils import db
from utils.helpers import mention_html, get_chat_admins
from utils.texts import t
from utils.scheduler import update_quiz_time
import logging

router = Router()
logger = logging.getLogger(__name__)

QUIZBOT_USERNAMES = ["quizbot", "quiz_bot", "testbot", "testmasterbot"]

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def quiz_activity_monitor(message: Message):
    """Monitor QuizBot activity"""
    if not message.from_user:
        return
    
    username = message.from_user.username or ""
    
    # Detect quiz bot activity
    if username.lower() in QUIZBOT_USERNAMES or message.from_user.is_bot:
        if message.poll or (message.text and any(kw in (message.text or "").lower() 
                                                   for kw in ["test", "quiz", "savol", "вопрос"])):
            update_quiz_time()
            logger.info(f"Quiz activity detected in {message.chat.id}")
    
    # Check if quiz poll ended
    if message.poll and message.poll.is_closed:
        await notify_admins_quiz_ended(message)

async def notify_admins_quiz_ended(message: Message):
    """Notify admins that quiz/poll ended"""
    chat_id = message.chat.id
    lang = db.get_bot_lang()
    
    try:
        admins = await get_chat_admins(message.bot, chat_id)
        mentions = " ".join([
            f'<a href="tg://user?id={admin_id}">Admin</a>'
            for admin_id in admins
        ])
        
        if mentions:
            text = f"📋 Test/So'rovnoma tugadi!\n\n{t('quiz_alert', lang)}\n\n👥 {mentions}"
            await message.answer(text, parse_mode="HTML")
            update_quiz_time()
    except Exception as e:
        logger.error(f"Quiz notify error: {e}")
