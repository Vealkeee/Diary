from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, F

from src.db.models import Group, Student
from sqlalchemy import select, and_

from src.handlers.registration.headmans.password import generate_password
from src.keyboards import headman_main

import requests

router = Router()

@router.callback_query(F.data == "headman")
async def createHeadman(call: CallbackQuery, db_pool):

    await call.answer()

    with db_pool() as db:

        stmt1 = (
            select(Student.first_name, Student.second_name, Student.group_name).
            where(Student.tgID == call.from_user.id)
        )

        first_name = db.execute(stmt1).all()[0][0]
        second_name = db.execute(stmt1).all()[0][1]
        group_name = db.execute(stmt1).all()[0][2]
        headman_pw = generate_password()
        headman_tgID = call.from_user.id

        stmt2 = (
                select(Group.group_name).
                where(and_(Group.headman_name.is_not(None), Group.group_name == group_name))
            )

        value = db.scalar(stmt2)

        if not value:

            json = {
                "group_name": group_name,
                "headman_name": first_name,
                "headman_second_name": second_name,
                "headman_pw": headman_pw,
                "headman_tgID":  headman_tgID
            }
            
            requests.post(url="http://127.0.0.1:7272/college/data/headman", json=json)
            await call.message.answer(f"✅ <b>УСПЕХ</b>\n\nАвторизация прошла успешно.\nПароль от аккаунта: <code>{headman_pw}</code>", parse_mode=ParseMode.HTML)
            await call.message.answer("🎓 <b>Главное меню</b>", parse_mode=ParseMode.HTML, reply_markup=headman_main)
        else:
            kb = InlineKeyboardBuilder()
            kb.button(text="✨ Ввести пароль", callback_data="PW_input")
            keyboard = kb.as_markup()
            await call.message.answer(f"❌ <b>ОТКАЗАНО</b>\n\nВ вашей группе уже есть староста.", parse_mode=ParseMode.HTML, reply_markup=keyboard)