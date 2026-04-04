import os
import asyncio

from dotenv import load_dotenv

from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot

from sqlalchemy import select, update
from src.db.models import Group, Student
from src.db.engine import localSession
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()
load_dotenv()
TOKEN = os.getenv("BOT")
bot = Bot(TOKEN)
message_ids = []

@router.callback_query(F.data == "student")
async def CreateConnectionKB(call: CallbackQuery, db_pool):

    await call.answer()
    
    kb = InlineKeyboardBuilder()
    tgID = call.from_user.id

    with db_pool() as db:

        getStatus = (
            select(Student.connected).
            where(Student.tgID == tgID)
        )

        status = db.scalar(getStatus)

        if status == None:

            stmt1 = (
                select(Student.group_name).
                where(Student.tgID == tgID)
            )

            group_name = db.scalar(stmt1)

            stmt2 = (
                select(Group.headman_name, Group.headman_second_name, Group.headman_tgID).
                where(Group.group_name == group_name)
            )

            try:
                headmanName, headmanSecondName, HeadmanTGid = db.execute(stmt2).first()
                kb.button(text=f"{headmanName} {headmanSecondName}", callback_data=f"connect:{HeadmanTGid}")
                keyboard = kb.as_markup()
                await call.message.answer("<b>🎄 ПРИВЯЗКА</b>\n\nДля <b>отправки привязки</b> к старосте, нажмите снизу на его инициалы... Через <b>24 часа</b> введите комманду старт...", parse_mode=ParseMode.HTML, reply_markup=keyboard)
            except Exception:
                bot_message = await call.message.answer("<b>🎄 ПРИВЯЗКА</b>\n\nВ вашей группе отсутствует староста... Попробуйте позже.", parse_mode=ParseMode.HTML)
                message_ids.append(bot_message.message_id)
        elif status == True:
            bot_message = await call.message.answer("<b>🎄 ПРИВЯЗКА</b>\n\nАккаунт уже <b>привязан</b> к старосте...", parse_mode=ParseMode.HTML)
            message_ids.append(bot_message.message_id)
        else:
            bot_message = await call.message.answer("<b>🎄 ПРИВЯЗКА</b>\n\nАккаунт находится в процессе привязки...", parse_mode=ParseMode.HTML)
            message_ids.append(bot_message.message_id)
    
    chat_id = call.message.chat.id

    await asyncio.sleep(5)

    await bot.delete_messages(chat_id, message_ids)

@router.callback_query(F.data.contains("connect:"))
async def connectStudent(call: CallbackQuery, db_pool):

    await call.answer()

    with db_pool() as db:

        updateStudentState = (
            update(Student).
            where(Student.tgID == call.from_user.id).
            values(connected=False)
        )

        db.execute(updateStudentState)
        db.commit()

        await call.message.answer("<b>🎄 ПРИВЯЗКА</b>\n\nЗапрос на привязку отправлен.", parse_mode=ParseMode.HTML)