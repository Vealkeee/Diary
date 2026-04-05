import os

from dotenv import load_dotenv

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import requests

load_dotenv()
TOKEN = os.getenv("BOT")
router = Router()
bot = Bot(TOKEN)

class Form(StatesGroup):
    math = State()
    biology = State()
    russian = State()
    informatics = State()
    physics = State()
    literature = State()
    history = State()
    english = State()
    physic_culture = State()
    social_science = State()
    opd = State()

message_ids = []

# Copy and paste world

@router.callback_query(F.data == "WriteGrades")
async def UpdateSG_keyboard(call: CallbackQuery, state: FSMContext):
    call.answer()
    await state.set_state(Form.math)
    bot_message = await call.message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по математике.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.math)
async def process_math(message: Message, state: FSMContext):
    await state.update_data(math=message.text)
    await state.set_state(Form.biology)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>биологии</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.biology)
async def process_biology(message: Message, state: FSMContext):
    await state.update_data(biology=message.text)
    await state.set_state(Form.russian)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>русскому языку</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.russian)
async def process_russian(message: Message, state: FSMContext):
    await state.update_data(russian=message.text)
    await state.set_state(Form.informatics)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>информатике</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.informatics)
async def process_informatics(message: Message, state: FSMContext):
    await state.update_data(informatics=message.text)
    await state.set_state(Form.physics)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>физике</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.physics)
async def process_physics(message: Message, state: FSMContext):
    await state.update_data(physics=message.text)
    await state.set_state(Form.literature)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>литературе</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.literature)
async def process_literature(message: Message, state: FSMContext):
    await state.update_data(literature=message.text)
    await state.set_state(Form.history)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>истории</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.history)
async def process_history(message: Message, state: FSMContext):
    await state.update_data(history=message.text)
    await state.set_state(Form.english)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>английскому языку</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.english)
async def process_english(message: Message, state: FSMContext):
    await state.update_data(english=message.text)
    await state.set_state(Form.physic_culture)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>физкультуре</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.physic_culture)
async def process_physic_culture(message: Message, state: FSMContext):
    await state.update_data(physic_culture=message.text)
    await state.set_state(Form.social_science)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>обществознанию</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.social_science)
async def process_social_science(message: Message, state: FSMContext):
    await state.update_data(social_science=message.text)
    await state.set_state(Form.opd)
    bot_message = await message.answer("<b>📝 ЗАПОЛНЕНИЕ ЖУРНАЛА</b>\n\nВведите все оценки студента по <b>ОПД</b>.", parse_mode=ParseMode.HTML)
    message_ids.append(bot_message.message_id)

@router.message(Form.opd)
async def process_opd(message: Message, state: FSMContext):
    await state.update_data(opd=message.text)

    data = await state.get_data()

    user_id = data.get("userID")
    math = data.get("math")
    biology = data.get("biology")
    russian = data.get("russian")
    informatics = data.get("informatics")
    physics = data.get("physics")
    literature = data.get("literature")
    history = data.get("history")
    english = data.get("english")
    physic_culture = data.get("physic_culture")
    social_science = data.get("social_science")
    opd = data.get("opd")

    chat_id = message.chat.id

    json = {
        "student_id": user_id,
        "math": math,
        "biology": biology,
        "russian": russian,
        "informatics": informatics,
        "physics": physics,
        "literature": literature,
        "history": history,
        "english": english,
        "physic_culture": physic_culture,
        "social_science": social_science,
        "opd": opd
    }

    response = requests.post("http://127.0.0.1:7272/college/data/grades", json=json)

    await bot.delete_messages(chat_id, message_ids)
    await message.answer("✅ <b>Все данные сохранены!</b>", parse_mode=ParseMode.HTML)
    await state.clear()