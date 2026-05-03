from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random
from utils.keyboards import games_menu_kb, back_kb, trivia_answer_kb
from utils.texts import t
from utils import db
import logging

router = Router()
logger = logging.getLogger(__name__)

class GameState(StatesGroup):
    math_game = State()
    word_game = State()
    riddle_game = State()

# English trivia questions
TRIVIA_QUESTIONS = [
    {"q": "What is the past tense of 'go'?", "options": ["goed", "went", "gone", "going"], "correct": 1},
    {"q": "Which sentence is correct?", "options": ["She don't like it", "She doesn't like it", "She not like it", "She didn't liked it"], "correct": 1},
    {"q": "What does 'nevertheless' mean?", "options": ["However", "Therefore", "Although", "Because"], "correct": 0},
    {"q": "Choose the correct form: 'I ___ here since 2020'", "options": ["am", "was", "have been", "had been"], "correct": 2},
    {"q": "What is the plural of 'child'?", "options": ["childs", "children", "childrens", "child's"], "correct": 1},
    {"q": "Which word is an adverb?", "options": ["quick", "quickly", "quickness", "quicken"], "correct": 1},
    {"q": "What does 'ubiquitous' mean?", "options": ["rare", "everywhere", "hidden", "unique"], "correct": 1},
    {"q": "Choose correct: 'Neither of them ___ ready'", "options": ["are", "is", "were", "have"], "correct": 1},
    {"q": "What is the synonym of 'happy'?", "options": ["sad", "angry", "joyful", "tired"], "correct": 2},
    {"q": "What comes after 'if I were you'?", "options": ["I will", "I would", "I should", "I could"], "correct": 1},
    {"q": "What is the antonym of 'ancient'?", "options": ["old", "modern", "historical", "classic"], "correct": 1},
    {"q": "'She has been studying' - this is which tense?", "options": ["Present Perfect", "Past Continuous", "Present Perfect Continuous", "Future Perfect"], "correct": 2},
]

RIDDLES_UZ = [
    {"q": "Kunduz kecha ko'r, kechasi ko'radi. Bu nima?", "a": "Yulduz"},
    {"q": "Oyoqsiz yuguradi, qo'lsiz ushlaydi. Bu nima?", "a": "Daryo"},
    {"q": "Ko'zi yo'q, ammo hamma narsani ko'radi. Bu nima?", "a": "Kamera"},
    {"q": "Qancha ko'p olsang, shuncha ko'p qoladi. Bu nima?", "a": "Bilim"},
    {"q": "Milliard odam ishlatadi, lekin hech kim uni yuvmaydi. Bu nima?", "a": "Til (Language)"},
    {"q": "Bitta oyog'i bor, lekin yuguradi. Bu nima?", "a": "Vaqt"},
]

MATH_QUESTIONS = [
    (lambda: (a := random.randint(10, 99), b := random.randint(10, 99), f"{a} + {b} = ?", a + b)),
    (lambda: (a := random.randint(10, 99), b := random.randint(1, a), f"{a} - {b} = ?", a - b)),
    (lambda: (a := random.randint(2, 12), b := random.randint(2, 12), f"{a} × {b} = ?", a * b)),
]

WORD_GAMES = [
    {"word": "APPLE", "hint": "Meva (Fruit)"},
    {"word": "HAPPY", "hint": "Xursand bo'lmoq (To feel joy)"},
    {"word": "LEARN", "hint": "O'rganmoq (To study)"},
    {"word": "SPEAK", "hint": "Gapirmoq (To talk)"},
    {"word": "WRITE", "hint": "Yozmoq (To put words on paper)"},
    {"word": "SMART", "hint": "Aqlli (Intelligent)"},
    {"word": "BRAVE", "hint": "Jasur (Courageous)"},
    {"word": "DREAM", "hint": "Orzu (Wish/Sleep vision)"},
]

@router.callback_query(F.data == "games")
async def games_menu(callback: CallbackQuery):
    await callback.message.edit_text("🎮 <b>O'yinlar Bo'limi</b>\n\nO'yin tanlang:", 
                                      reply_markup=games_menu_kb(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "game_trivia")
async def trivia_game(callback: CallbackQuery):
    db.increment_stat("total_games")
    q = random.choice(TRIVIA_QUESTIONS)
    q_id = random.randint(1000, 9999)
    
    await callback.message.edit_text(
        f"🧠 <b>Trivia Quiz</b>\n\n❓ {q['q']}",
        reply_markup=trivia_answer_kb(q['options'], q['correct'], q_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("trivia_"))
async def trivia_answer(callback: CallbackQuery):
    parts = callback.data.split("_")
    q_id, chosen, correct = parts[1], int(parts[2]), int(parts[3])
    
    if chosen == correct:
        db.add_user_score(callback.from_user.id, 10)
        total = db.get_user_score(callback.from_user.id)
        text = f"✅ <b>To'g'ri!</b> +10 ball\n💰 Jami: {total} ball\n\nQayta o'ynash uchun tugmani bosing!"
    else:
        letters = ['A', 'B', 'C', 'D']
        text = f"❌ <b>Noto'g'ri!</b>\n✅ To'g'ri javob: <b>{letters[correct]}</b>"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yana O'yna", callback_data="game_trivia")],
        [InlineKeyboardButton(text="◀️ O'yinlar", callback_data="games")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer("✅ Javob qabul qilindi!" if chosen == correct else "❌ Noto'g'ri!")

@router.callback_query(F.data == "game_math")
async def math_game(callback: CallbackQuery, state: FSMContext):
    db.increment_stat("total_games")
    a = random.randint(10, 50)
    b = random.randint(10, 50)
    op = random.choice(["+", "-", "×"])
    
    if op == "+":
        answer = a + b
    elif op == "-":
        answer = abs(a - b)
        a, b = max(a, b), min(a, b)
    else:
        answer = a * b
    
    await state.set_state(GameState.math_game)
    await state.update_data(answer=answer)
    
    await callback.message.edit_text(
        f"🔢 <b>Matematik Duel</b>\n\n"
        f"❓ <b>{a} {op} {b} = ?</b>\n\n"
        f"Javobingizni yozing:",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(GameState.math_game)
async def math_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    correct = data.get("answer")
    
    try:
        user_ans = int(message.text.strip())
    except:
        await message.reply("❗ Iltimos raqam yozing!")
        return
    
    await state.clear()
    
    if user_ans == correct:
        db.add_user_score(message.from_user.id, 15)
        total = db.get_user_score(message.from_user.id)
        await message.reply(
            f"✅ <b>Ajoyib! To'g'ri!</b> +15 ball\n💰 Jami: {total} ball",
            reply_markup=back_kb("games"), parse_mode="HTML"
        )
    else:
        await message.reply(
            f"❌ <b>Noto'g'ri!</b>\n✅ To'g'ri javob: <b>{correct}</b>",
            reply_markup=back_kb("games"), parse_mode="HTML"
        )

@router.callback_query(F.data == "game_word")
async def word_game(callback: CallbackQuery, state: FSMContext):
    db.increment_stat("total_games")
    game = random.choice(WORD_GAMES)
    word = game["word"]
    hint = game["hint"]
    
    # Shuffle letters
    letters = list(word)
    random.shuffle(letters)
    scrambled = " ".join(letters)
    
    await state.set_state(GameState.word_game)
    await state.update_data(answer=word)
    
    await callback.message.edit_text(
        f"📝 <b>So'z O'yini</b>\n\n"
        f"Harflarni tartibga soling:\n"
        f"🔀 <b>{scrambled}</b>\n\n"
        f"💡 Izoh: {hint}\n\n"
        f"Javobingizni yozing:",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(GameState.word_game)
async def word_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    correct = data.get("answer", "")
    
    await state.clear()
    
    if message.text.strip().upper() == correct.upper():
        db.add_user_score(message.from_user.id, 20)
        total = db.get_user_score(message.from_user.id)
        await message.reply(
            f"✅ <b>Zo'r! To'g'ri!</b> +20 ball\n💰 Jami: {total} ball",
            reply_markup=back_kb("games"), parse_mode="HTML"
        )
    else:
        await message.reply(
            f"❌ <b>Noto'g'ri!</b>\n✅ To'g'ri so'z: <b>{correct}</b>",
            reply_markup=back_kb("games"), parse_mode="HTML"
        )

@router.callback_query(F.data == "game_luck")
async def luck_game(callback: CallbackQuery):
    db.increment_stat("total_games")
    result = random.randint(1, 6)
    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"][result - 1]
    
    points = result * 5
    db.add_user_score(callback.from_user.id, points)
    total = db.get_user_score(callback.from_user.id)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Yana Tashlash", callback_data="game_luck")],
        [InlineKeyboardButton(text="◀️ O'yinlar", callback_data="games")]
    ])
    
    await callback.message.edit_text(
        f"🍀 <b>Omad Toshi</b>\n\n"
        f"🎲 Zar: {emoji}\n"
        f"🎯 Natija: <b>{result}</b>\n"
        f"✨ +{points} ball!\n"
        f"💰 Jami: {total} ball",
        reply_markup=kb, parse_mode="HTML"
    )
    await callback.answer(f"🎲 {result} chiqdi!")

@router.callback_query(F.data == "game_riddle")
async def riddle_game(callback: CallbackQuery, state: FSMContext):
    db.increment_stat("total_games")
    riddle = random.choice(RIDDLES_UZ)
    
    await state.set_state(GameState.riddle_game)
    await state.update_data(answer=riddle["a"].lower())
    
    await callback.message.edit_text(
        f"🎭 <b>Topishmoq</b>\n\n"
        f"❓ {riddle['q']}\n\n"
        f"Javobingizni yozing:",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(GameState.riddle_game)
async def riddle_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    correct = data.get("answer", "")
    await state.clear()
    
    if message.text.strip().lower() in correct.lower() or correct.lower() in message.text.strip().lower():
        db.add_user_score(message.from_user.id, 25)
        total = db.get_user_score(message.from_user.id)
        await message.reply(
            f"✅ <b>Barakalla! To'g'ri!</b> +25 ball\n💰 Jami: {total} ball",
            reply_markup=back_kb("games"), parse_mode="HTML"
        )
    else:
        await message.reply(
            f"❌ <b>Noto'g'ri!</b>\n✅ To'g'ri javob: <b>{correct.title()}</b>",
            reply_markup=back_kb("games"), parse_mode="HTML"
        )

@router.callback_query(F.data == "game_knowledge")
async def knowledge_game(callback: CallbackQuery):
    """General knowledge questions"""
    questions = [
        {"q": "Ingliz tili qaysi mamlakatning ona tili?", "options": ["Fransiya", "Buyuk Britaniya", "Germaniya", "Italiya"], "correct": 1},
        {"q": "Ingliz tilida nechta harf bor?", "options": ["24", "25", "26", "27"], "correct": 2},
        {"q": "'Oxford Dictionary' qachon yaratilgan?", "options": ["1884", "1900", "1850", "1920"], "correct": 0},
        {"q": "Ingliz tilida eng ko'p ishlatiladigan so'z?", "options": ["the", "a", "is", "and"], "correct": 0},
    ]
    
    db.increment_stat("total_games")
    q = random.choice(questions)
    q_id = random.randint(1000, 9999)
    
    await callback.message.edit_text(
        f"🎯 <b>Bilimdon</b>\n\n❓ {q['q']}",
        reply_markup=trivia_answer_kb(q['options'], q['correct'], q_id),
        parse_mode="HTML"
    )
    await callback.answer()
