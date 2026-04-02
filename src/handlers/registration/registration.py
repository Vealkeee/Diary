from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, F

import requests

from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.db.models import Student
from sqlalchemy import select

from redis import Redis

errorStatus = [500, 422]
restart = ["incorrect", "begginFromStart"]

router = Router()
redis = Redis(host="localhost", port="6379", decode_responses=True)

class Schema(StatesGroup):
    first_name = State()
    second_name = State()
    group_name = State()
    ensure = State()

@router.callback_query(F.data == "agreement")
async def getName(call: CallbackQuery, state: FSMContext, db_pool):
    
    attempts = int(redis.get("attempt"))
    if attempts == 5:
        await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nОтправлено 5 запросов в течение 2-х минут. Попробуйте снова через 24 часа.", parse_mode=ParseMode.HTML)
    else:
        with db_pool() as session:

            userID = call.from_user.id
            stmt = (select(Student.tgID).
                    where(Student.tgID == userID))
            
            scalarID = session.scalar(stmt)

        if not scalarID:
            await call.answer()
            await state.set_state(Schema.first_name)
            await call.message.answer("<b>✨ ИМЯ СТУДЕНТА</b>\n\nПожалуйста введите своё настоящее имя.", parse_mode=ParseMode.HTML)
        else:
            await call.answer()
            await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nВы уже <b>АВТОРИЗОВАНЫ.</b>", parse_mode=ParseMode.HTML)

@router.message(Schema.first_name)
async def getFam(message: Message, state: FSMContext):
    await state.set_state(Schema.second_name)
    await state.update_data(firstName=message.text,
                            tgID=message.from_user.id,
                            chatID=message.chat.id)
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Вернуться", callback_data="back1")
    keyboard = kb.as_markup()
    await message.answer("<b>✨ ФАМИЛИЯ СТУДЕНТА</b>\n\nПожалуйста введите свою настоящую фамилию.", parse_mode=ParseMode.HTML, reply_markup=keyboard)

@router.message(Schema.second_name)
async def getGroup(message: Message, state: FSMContext):
    await state.set_state(Schema.group_name)
    await state.update_data(secondName=message.text)
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Вернуться", callback_data="back2")
    keyboard = kb.as_markup()
    await message.answer(f"<b>✨ ГРУППА СТУДЕНТА</b>\n\nПожалуйста введите свою учебную группу.", parse_mode=ParseMode.HTML, reply_markup=keyboard)

@router.message(Schema.group_name)
async def EnsureTheData(message: Message, state: FSMContext):
    await state.set_state(Schema.ensure)
    await state.update_data(group=message.text)

    data = await state.get_data()

    firstName = data.get("firstName")
    secondName = data.get("secondName")
    groupName = data.get("group")

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Корректно", callback_data="correct")
    kb.button(text="❌ Не корректно", callback_data="incorrect")
    kb.adjust(1, 1)
    ensure_kb = kb.as_markup()

    await message.answer(f"<b>‼️ ПРОВЕРКА</b>\n\nПожалуйста проверьте данные.\n\n"\
                         f"<b>Имя</b>: {firstName}\n<b>Фамилия</b>: {secondName}\n<b>Группа</b>: {groupName}", parse_mode=ParseMode.HTML, reply_markup=ensure_kb)


@router.callback_query(F.data.in_(restart))
async def uploadUser(call: CallbackQuery, state: FSMContext):
    attempts = int(redis.get("attempt"))
    if attempts == 5:
        await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nОтправлено 5 запросов в течение 2-х минут. Попробуйте снова через 24 часа.", parse_mode=ParseMode.HTML)
    else:
        await call.answer()
        await state.clear()
        await state.set_state(Schema.first_name)
        await call.message.answer(f"<b>✨ ИМЯ СТУДЕНТА</b>\n\nПожалуйста введите своё настоящее имя.", parse_mode=ParseMode.HTML)

@router.callback_query(F.data == "correct")
async def uploadUser(call: CallbackQuery, state: FSMContext, db_pool):
    await call.answer()

    data = await state.get_data()

    firstName = data.get("firstName")
    secondName = data.get("secondName")
    groupName = data.get("group")
    tgID = data.get("tgID")
    chat_id = data.get("chatID")

    with db_pool() as db:

        stmt = (
            select(Student).
            where(Student.first_name == firstName, Student.second_name == secondName)
        )

        value = db.scalar(stmt)

    if not value:
        json = {
            "first_name": firstName,
            "second_name": secondName,
            "group_name": groupName,
            "tgID": tgID,
            "chat_id": chat_id
        }

        response = requests.post("http://127.0.0.1:7272/college/data/student", json=json)

        if response.status_code not in errorStatus:
            kb = InlineKeyboardBuilder()
            kb.button(text="🎓 Студент", callback_data="student")
            kb.button(text="💼 Староста", callback_data="headman")
            kb.adjust(1, 1)
            ensure_kb = kb.as_markup()
            await call.message.answer("<b>✨ ВЫБОР РОЛИ</b>\n\nПожалуйста выберите свою роль.", parse_mode=ParseMode.HTML, reply_markup=ensure_kb)
        else:
            attempts = int(redis.get("attempt")) + 1
            print(attempts)
            if attempts == 5:
                redis.set("attempt", attempts, ex=86400)
                kb = InlineKeyboardBuilder()
                kb.button(text="📝 Начать сначала", callback_data="begginFromStart")
                reAuth_kb = kb.as_markup()

                await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nНеправильный ввод данных, либо вы превысили лимит отправки запросов ( 5/2мин ). Попробуйте ещё.", parse_mode=ParseMode.HTML, reply_markup=reAuth_kb)
            else:
                await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nОтправлено 5 запросов в течение 2-х минут. Попробуйте снова через 24 часа.", parse_mode=ParseMode.HTML)
    else:
        await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nПользователь с таким именем и фамилией уже существует.", parse_mode=ParseMode.HTML)