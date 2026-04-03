from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, F

from src.db.models import Group, Student
from sqlalchemy import select, and_

from src.keyboards import headman_main

router = Router()

class pwAuth(StatesGroup):
    stage1 = State()
    stage2 = State()

@router.callback_query(F.data == "PW_input")
async def createHeadman(call: CallbackQuery, state: FSMContext):

    await call.answer()
    await state.set_state(pwAuth.stage1)
    await call.message.answer("<b>Введите пароль ...</b>", parse_mode=ParseMode.HTML)

@router.message(pwAuth.stage1)
async def UserPWinput(message: Message, state: FSMContext, db_pool):

    await state.set_state(pwAuth.stage2)
    await state.update_data(pw=message.text)

    data = await state.get_data()
    password = data.get("pw")

    with db_pool() as db:

        stmt1 = (
            select(Student.group_name).
            where(Student.tgID == message.from_user.id)
        )

        group_name = db.scalar(stmt1)
    
        stmt2 = (
                select(Group.headman_pw).
                where(Group.group_name == group_name)
            )

        value = db.scalar(stmt2)

        if value == password:
            await message.answer("🎓 <b>Главное меню</b>\n\nЗдесь вы можете посмотреть оценки, домашнее задание и расписание.\n\nА также, внести изменения в данные категории как староста.", parse_mode=ParseMode.HTML, reply_markup=headman_main)
        else:
            await message.answer("❌ <b>ОТКАЗАНО</b>", parse_mode=ParseMode.HTML)