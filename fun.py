from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import random
from utils.keyboards import fun_menu_kb, back_kb
from utils.texts import t
from utils import db

router = Router()

JOKES = {
    "uz": [
        "😂 Ingliz tili o'qituvchisi: 'I before E except after C'\nO'quvchi: 'Weird!'\nO'qituvchi: '...ha, weird...'",
        "😂 - Inglizcha 'fish' ni qanday imlolash mumkin?\n- 'GHOTI'!\n'gh' kabi 'laugh'da, 'o' kabi 'women'da, 'ti' kabi 'nation'da!",
        "😂 Grammatika o'qituvchisi: 'Ikki salbiy narsani ayting.'\nO'quvchi: 'Bilmayman, bilmayman.'",
        "😂 Men ingliz tilini bilaman deb o'yladim... Keyin ona tilim so'raldi.",
        "😂 Muallim: 'Jumlada present perfect ishlating'\nO'quvchi: 'I have not done my homework'\nMuallim: '... Hech bo'lmasa grammatikasi to'g'ri'",
    ],
    "ru": [
        "😂 Учитель: 'Составьте предложение с глаголом would'\nУченик: 'I would like to sleep in class'\nУчитель: '...'",
        "😂 Почему программисты путают Хэллоуин и Рождество?\nПотому что 31 Oct = 25 Dec!",
        "😂 - Выучи английский!\n- Зачем?\n- Будешь читать ошибки в коде на языке оригинала!",
    ],
    "en": [
        "😂 Teacher: 'Name something that is hot and makes people happy'\nStudent: 'My exam results being cancelled'",
        "😂 Why do programmers prefer dark mode? Because light attracts bugs!",
        "😂 Student: 'Can I use the bathroom?'\nTeacher: 'It's MAY I'\nStudent: 'OK may I?'\nTeacher: 'No, sit down'",
    ]
}

FACTS = [
    "🤯 Ingliz tili dunyoda eng ko'p ishlatiladigan 2-til hisoblanadi (1.5 mlrd kishi).",
    "🤯 'Set' so'zi ingliz tilida eng ko'p ma'noga ega - 464 ta!",
    "🤯 'Dreamt' - ingliz tilida 'mt' bilan tugaydigan yagona so'z!",
    "🤯 Dunyodagi barcha kompyuter kodlarining 80% ingliz tilida yozilgan.",
    "🤯 'Rhythm' - ingliz tilidagi unlisiz eng uzun so'z (6 harf).",
    "🤯 'Strengths' - ingliz tilidagi bitta unli bilan tugaydigan eng uzun so'z.",
    "🤯 Shakespeare 1700 dan ortiq yangi so'z yaratgan (bedroom, lonely, generous...).",
    "🤯 Ingliz tilida har 98 daqiqada yangi so'z paydo bo'ladi.",
    "🤯 'Go' ingliz tilidagi eng qisqa to'liq jumla hisoblanadi.",
    "🤯 'I am' dunyodagi eng qisqa to'liq jumlalardan biri.",
]

QUOTES = [
    "💡 'The limits of my language mean the limits of my world.' — Ludwig Wittgenstein",
    "💡 'A different language is a different vision of life.' — Federico Fellini",
    "💡 'One language sets you in a corridor for life. Two languages open every door along the way.' — Frank Smith",
    "💡 'Language is the road map of a culture.' — Rita Mae Brown",
    "💡 'To have another language is to possess a second soul.' — Charlemagne",
    "💡 'Learning another language is not only learning different words, but different ways to think.' — Flora Lewis",
    "💡 'The man who does not know other languages knows nothing of his own.' — Goethe",
]

HOROSCOPES = {
    "♈ Qo'y (Aries)": "Bugun ingliz tilida yangi so'z o'rganishga zo'r kun!",
    "♉ Buzoq (Taurus)": "Bir ingliz filmini tomosha qilish g'oyasi yaxshi.",
    "♊ Egizaklar (Gemini)": "Bugun ingliz tilida suhbatlashishga urinib ko'ring!",
    "♋ Qisqichbaqa (Cancer)": "Grammar qoidalarini takrorlash vaqti keldi.",
    "♌ Sher (Leo)": "Bugun ingliz tilidagi podcast tinglash omadingizni oshiradi.",
    "♍ Boshoq (Virgo)": "Lug'at o'qish bugun sizga katta foyda beradi.",
    "♎ Tarozi (Libra)": "Ingliz tilida xat yozish mashqlarini bajaring.",
    "♏ Chayan (Scorpio)": "Bugun ingliz tilidagi kitob boshlab ko'ring.",
    "♐ Yoy (Sagittarius)": "Online ingliz tili kursi bugun siz uchun.",
    "♑ Tog' echkisi (Capricorn)": "Tartibli o'rganish bugun muvaffaqiyat keltiradi.",
    "♒ Suv quyuvchi (Aquarius)": "Ingliz tilidagi yangi qo'shiq o'rganing!",
    "♓ Baliq (Pisces)": "Bugun intuitsiyangizga ishoning - inglizcha gapirishda dadil bo'ling!",
}

TIPS = [
    "☀️ <b>Kun maslahati:</b> Har kuni kamida 10 ta yangi inglizcha so'z o'rganing!",
    "☀️ <b>Kun maslahati:</b> Inglizcha film ko'rayotganda subtitrlarsiz ko'rishga urinib ko'ring.",
    "☀️ <b>Kun maslahati:</b> Inglizcha fikrlashga harakat qiling, keyin gapirishga o'ting.",
    "☀️ <b>Kun maslahati:</b> Mirror speaking - oyna oldida inglizcha gaping, artikulyatsiyani yaxshilaysiz.",
    "☀️ <b>Kun maslahati:</b> Shadowing texnikasidan foydalaning - native speaker'larni taqlid qiling.",
    "☀️ <b>Kun maslahati:</b> Spaced repetition bilan so'z eslab qoling (Anki app).",
    "☀️ <b>Kun maslahati:</b> Har kuni 30 daqiqa inglizcha audio tinglang.",
]

@router.callback_query(F.data == "fun")
async def fun_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "😄 <b>Qiziqarli Bo'lim</b>\n\nNimani xohlaysiz?",
        reply_markup=fun_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "fun_joke")
async def fun_joke(callback: CallbackQuery):
    lang = db.get_bot_lang()
    jokes = JOKES.get(lang, JOKES["uz"])
    joke = random.choice(jokes)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😂 Yana Latifa", callback_data="fun_joke")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="fun")]
    ])
    
    await callback.message.edit_text(joke, reply_markup=kb, parse_mode="HTML")
    await callback.answer("😂")

@router.callback_query(F.data == "fun_fact")
async def fun_fact(callback: CallbackQuery):
    fact = random.choice(FACTS)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤯 Yana Fakt", callback_data="fun_fact")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="fun")]
    ])
    
    await callback.message.edit_text(fact, reply_markup=kb, parse_mode="HTML")
    await callback.answer("🤯")

@router.callback_query(F.data == "fun_quote")
async def fun_quote(callback: CallbackQuery):
    quote = random.choice(QUOTES)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Yana Iqtibos", callback_data="fun_quote")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="fun")]
    ])
    
    await callback.message.edit_text(quote, reply_markup=kb, parse_mode="HTML")
    await callback.answer("💡")

@router.callback_query(F.data == "fun_horoscope")
async def fun_horoscope(callback: CallbackQuery):
    sign, text = random.choice(list(HOROSCOPES.items()))
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Boshqa Burj", callback_data="fun_horoscope")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="fun")]
    ])
    
    await callback.message.edit_text(
        f"⭐ <b>Kunlik Horoscope</b>\n\n{sign}\n\n{text}",
        reply_markup=kb, parse_mode="HTML"
    )
    await callback.answer(sign)

@router.callback_query(F.data == "fun_tip")
async def fun_tip(callback: CallbackQuery):
    tip = random.choice(TIPS)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☀️ Boshqa Maslahat", callback_data="fun_tip")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="fun")]
    ])
    
    await callback.message.edit_text(tip, reply_markup=kb, parse_mode="HTML")
    await callback.answer("☀️")
