from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from utils.keyboards import main_menu_kb
from utils.texts import t
from utils import db
from config import ADMIN_ID
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def start_cmd(message: Message):
    user = message.from_user
    db.register_user(user.id, user.username, user.full_name)
    
    lang = db.get_bot_lang()
    
    # Check mandatory channels
    channels = db.get_mandatory_channels()
    if channels:
        from utils.helpers import check_mandatory_membership
        not_subscribed = await check_mandatory_membership(message.bot, user.id, channels)
        if not_subscribed:
            from utils.keyboards import join_channels_kb
            await message.answer(
                t("must_join", lang) + "\n" + "\n".join(not_subscribed),
                reply_markup=join_channels_kb(not_subscribed),
                parse_mode="HTML"
            )
            return
    
    text = t("welcome", lang, name=user.first_name)
    await message.answer(text, reply_markup=main_menu_kb(lang), parse_mode="HTML")

@router.message(Command("panel"))
async def admin_panel_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    from utils.keyboards import admin_panel_kb
    lang = db.get_bot_lang()
    await message.answer(t("admin_panel", lang), reply_markup=admin_panel_kb(), parse_mode="HTML")

@router.message(Command("help"))
async def help_cmd(message: Message):
    lang = db.get_bot_lang()
    from utils.keyboards import back_kb
    await message.answer(t("help_text", lang), reply_markup=back_kb(), parse_mode="HTML")

@router.callback_query(F.data == "main_menu")
async def main_menu_cb(callback: CallbackQuery):
    lang = db.get_bot_lang()
    await callback.message.edit_text(
        t("main_menu", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "help")
async def help_cb(callback: CallbackQuery):
    lang = db.get_bot_lang()
    from utils.keyboards import back_kb
    await callback.message.edit_text(
        t("help_text", lang),
        reply_markup=back_kb(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "check_joined")
async def check_joined_cb(callback: CallbackQuery):
    user = callback.from_user
    channels = db.get_mandatory_channels()
    lang = db.get_bot_lang()
    
    if channels:
        from utils.helpers import check_mandatory_membership
        from utils.keyboards import join_channels_kb
        not_subscribed = await check_mandatory_membership(callback.bot, user.id, channels)
        if not_subscribed:
            await callback.answer("❌ Hali barcha kanallarga a'zo bo'lmadingiz!", show_alert=True)
            return
    
    text = t("welcome", lang, name=user.first_name)
    await callback.message.edit_text(text, reply_markup=main_menu_kb(lang), parse_mode="HTML")
    await callback.answer("✅ Rahmat!")

@router.callback_query(F.data == "my_score")
async def my_score_cb(callback: CallbackQuery):
    user = callback.from_user
    lang = db.get_bot_lang()
    score = db.get_user_score(user.id)
    from utils.keyboards import back_kb
    await callback.message.edit_text(
        t("score_info", lang, name=user.first_name, score=score),
        reply_markup=back_kb(),
        parse_mode="HTML"
    )
    await callback.answer()
