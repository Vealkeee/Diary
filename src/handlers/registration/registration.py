import os
import asyncio
import logging

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot, BaseMiddleware

import requests

from dotenv import load_dotenv
from typing import Any, Callable, Dict, Awaitable
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.db.models import Student
from sqlalchemy import select

from redis import Redis

logging.basicConfig(level=logging.INFO, filename="logs\\messagesLog.log",
                    filemode="a", format='%(asctime)s - %(levelname)s - %(message)s')

errorStatus = [500, 422]
restart = ["incorrect", "begginFromStart"]

load_dotenv()

TOKEN = os.getenv("BOT")

router = Router()
redis = Redis(host="localhost", port="6379", decode_responses=True)
bot = Bot(TOKEN)

message_ids = []

class MessageIdCollectorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        message_ids.append(event.message_id)
        logging.info(f"Captured ID: {event.message_id}. Current list size: {len(message_ids)}")
        return await handler(event, data)
    
router.message.outer_middleware(MessageIdCollectorMiddleware())

class Schema(StatesGroup):
    first_name = State()
    second_name = State()
    group_name = State()
    ensure = State()

@router.callback_query(F.data == "agreement")
async def getName(call: CallbackQuery, state: FSMContext, db_pool):
    
    attempts = int(redis.get("attempt"))
    if attempts == 5:
        bot_message = await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nОтправлено 5 запросов в течение 2-х минут. Попробуйте снова через 24 часа.", parse_mode=ParseMode.HTML)
        message_ids.append(bot_message.message_id)
    else:
        with db_pool() as session:

            userID = call.from_user.id
            stmt = (select(Student.tgID).
                    where(Student.tgID == userID))
            
            scalarID = session.scalar(stmt)

        if not scalarID:
            await call.answer()
            await state.set_state(Schema.first_name)
            bot_message = await call.message.answer("<b>✨ ИМЯ СТУДЕНТА</b>\n\nПожалуйста введите своё настоящее имя.", parse_mode=ParseMode.HTML)
            message_ids.append(bot_message.message_id)
        else:
            await call.answer()
            bot_message = await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nВы уже <b>АВТОРИЗОВАНЫ.</b>", parse_mode=ParseMode.HTML)
            message_ids.append(bot_message.message_id)

@router.message(Schema.first_name)
async def getFam(message: Message, state: FSMContext):
    await state.set_state(Schema.second_name)
    await state.update_data(firstName=message.text,
                            tgID=message.from_user.id,
                            chatID=message.chat.id)
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Вернуться", callback_data="back1")
    keyboard = kb.as_markup()
    bot_message = await message.answer("<b>✨ ФАМИЛИЯ СТУДЕНТА</b>\n\nПожалуйста введите свою настоящую фамилию.", parse_mode=ParseMode.HTML, reply_markup=keyboard)
    message_ids.append(bot_message.message_id)

@router.message(Schema.second_name)
async def getGroup(message: Message, state: FSMContext):
    await state.set_state(Schema.group_name)
    await state.update_data(secondName=message.text)
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Вернуться", callback_data="back2")
    keyboard = kb.as_markup()
    bot_message = await message.answer(f"<b>✨ ГРУППА СТУДЕНТА</b>\n\nПожалуйста введите свою учебную группу.", parse_mode=ParseMode.HTML, reply_markup=keyboard)
    message_ids.append(bot_message.message_id)

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

    bot_message = await message.answer(f"<b>‼️ ПРОВЕРКА</b>\n\nПожалуйста проверьте данные.\n\n"\
                                       f"<b>Имя</b>: {firstName}\n<b>Фамилия</b>: {secondName}\n<b>Группа</b>: {groupName}", parse_mode=ParseMode.HTML, reply_markup=ensure_kb)
    message_ids.append(bot_message.message_id)

@router.callback_query(F.data.in_(restart))
async def uploadUser(call: CallbackQuery, state: FSMContext, db_pool):
    attempts = int(redis.get("attempt"))

    with db_pool() as db:
        
        stmt = (
            select(Student.register).
            where(Student.tgID == call.from_user.id)
        )

        value = db.scalar(stmt)

        if attempts == 5:
            bot_message = await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nОтправлено 5 запросов в течение 2-х минут. Попробуйте снова через 24 часа.", parse_mode=ParseMode.HTML)
            message_ids.append(bot_message.message_id)
        elif value == None:
            await call.answer()
            await state.clear()
            await state.set_state(Schema.first_name)
            bot_message = await call.message.answer(f"<b>✨ ИМЯ СТУДЕНТА</b>\n\nПожалуйста введите своё настоящее имя.", parse_mode=ParseMode.HTML)
            message_ids.append(bot_message.message_id)
        else:
            await call.answer()
            bot_message = await call.message.answer(f"<b>❌ ОТКАЗАНО</b>\n\nВы уже зарегистрированы.", parse_mode=ParseMode.HTML)
            message_ids.append(bot_message.message_id)

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
                "chat_id": chat_id,
                "register": True
            }

            response = requests.post("http://127.0.0.1:7272/college/data/student", json=json)

            if response.status_code not in errorStatus:
                kb = InlineKeyboardBuilder()
                kb.button(text="🎓 Студент", callback_data="student")
                kb.button(text="💼 Староста", callback_data="headman")
                kb.adjust(1, 1)
                ensure_kb = kb.as_markup()
                bot_message2 = await call.message.answer("<b>‼️ 15 СЕКУНД ДО ОЧИСТКИ</b>\n\n", parse_mode=ParseMode.HTML)
                bot_message1 = await call.message.answer("<b>✨ ВЫБОР РОЛИ</b>\n\nПожалуйста выберите свою роль.", parse_mode=ParseMode.HTML, reply_markup=ensure_kb)
                message_ids.append(bot_message1.message_id)
                message_ids.append(bot_message2.message_id)
                await asyncio.sleep(15)
                chat = bot_message1.chat.id
                await bot.delete_messages(chat, message_ids)
                await call.message.answer("<b>Введите комманду /start если меню не открылось. Или что бы проверить привязку аккаунта.</b>", parse_mode=ParseMode.HTML)
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
            bot_message = await call.message.answer("<b>❌ ОТКАЗАНО</b>\n\nПользователь с таким именем и фамилией уже существует.", parse_mode=ParseMode.HTML)
            message_ids.append(bot_message.message_id)