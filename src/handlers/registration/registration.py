from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, F

import requests

from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.db.models import Student
from sqlalchemy import select

errorStatus = [500, 422]

router = Router()

class Schema(StatesGroup):
    first_name = State()
    second_name = State()
    group_name = State()
    ensure = State()

@router.callback_query(F.data == "agreement")
async def getName(call: CallbackQuery, state: FSMContext, db_pool):

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
    await message.answer("<b>✨ ФАМИЛИЯ СТУДЕНТА</b>\n\nПожалуйста введите свою настоящую фамилию.", parse_mode=ParseMode.HTML)

@router.message(Schema.second_name)
async def getGroup(message: Message, state: FSMContext):
    await state.set_state(Schema.group_name)
    await state.update_data(secondName=message.text)
    await message.answer(f"<b>✨ ГРУППА СТУДЕНТА</b>\n\nПожалуйста введите свою учебную группу.", parse_mode=ParseMode.HTML)

@router.message(Schema.group_name)
async def getGroup(message: Message, state: FSMContext):
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


@router.callback_query(F.data == "incorrect")
async def uploadUser(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    await state.set_state(Schema.first_name)
    await call.message.answer(f"<b>✨ ИМЯ СТУДЕНТА</b>\n\nПожалуйста введите своё настоящее имя.", parse_mode=ParseMode.HTML)

@router.callback_query(F.data == "correct")
async def uploadUser(call: CallbackQuery, state: FSMContext):
    await call.answer()

    kb = InlineKeyboardBuilder()
    kb.button(text="🎓 Студент", callback_data="student")
    kb.button(text="💼 Староста", callback_data="headman")
    kb.adjust(1, 1)
    ensure_kb = kb.as_markup()

    data = await state.get_data()

    firstName = data.get("firstName")
    secondName = data.get("secondName")
    groupName = data.get("group")
    tgID = data.get("tgID")
    chat_id = data.get("chatID")

    json = {
        "first_name": firstName,
        "second_name": secondName,
        "group_name": groupName,
        "tgID": tgID,
        "chat_id": chat_id
    }

    response = requests.post("http://127.0.0.1:7272/college/data/student", json=json)

    if response.status_code not in errorStatus:
        await call.message.answer("<b>✨ ВЫБОР РОЛИ</b>\n\nПожалуйста выберите свою роль.", parse_mode=ParseMode.HTML, reply_markup=ensure_kb)
    else:
        kb = InlineKeyboardBuilder()
        kb.button(text="📝 Начать сначала", callback_data="begginFromStart")
        reAuth_kb = kb.as_markup()

        await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nНеправильный ввод данных, либо вы превысили лимит отправки запросов ( 5/2мин ). Попробуйте ещё.", parse_mode=ParseMode.HTML, reply_markup=reAuth_kb)