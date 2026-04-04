from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, F

from sqlalchemy import select, update, and_
from src.db.models import Student
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.callback_query(F.data == "studentConnections")
async def ConnectStudentToGroup(call: CallbackQuery, db_pool):

    await call.answer()
    
    kb = InlineKeyboardBuilder()

    with db_pool() as db:

        stmt1 = (
            select(Student.group_name).
            where(Student.tgID == call.from_user.id)
        )

        group = db.scalar(stmt1)

        stmt2 = (
            select(Student.tgID, Student.first_name, Student.second_name).
            where(and_(Student.group_name == group, Student.connected == False))
        )

        value = db.execute(stmt2).all()

        if not value:
            await call.message.answer(f"📶 <b>ПРИВЯЗКА</b>\n\nНа данный момент остутствуют пользователи для привязки.", parse_mode=ParseMode.HTML)
        else:
            for item in value:
                kb.button(text=f"{item[1]} {item[2]}", callback_data=f"verified:{item[0]}")
            kb.adjust(2, 2, repeat=True)
            keyboard = kb.as_markup()
            await call.message.answer(f"📶 <b>ПРИВЯЗКА</b>\n\nВыберите пользователя для привязки к группе...", reply_markup=keyboard, parse_mode=ParseMode.HTML)

    await call.message.answer()

@router.callback_query(F.data.contains("verified:"))
async def connectStudent(call: CallbackQuery, db_pool):

    await call.answer()

    user_id = int(call.data.split(":")[1])

    with db_pool() as db:

        updateStudentState = (
            update(Student).
            where(Student.tgID == user_id).
            values(connected=True)
        )

        db.execute(updateStudentState)
        db.commit()

        await call.message.answer("<b>🎄 ПРИВЯЗКА</b>\n\nПользователь теперь привязан к группе.", parse_mode=ParseMode.HTML)