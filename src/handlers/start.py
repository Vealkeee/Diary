from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from sqlalchemy import select
from src.db.models import Student

from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram import Router, F

router = Router()

@router.message(CommandStart())
async def welcome(message: Message, db_pool):

    with db_pool() as session:

        userID = message.from_user.id
        stmt = (select(Student.tgID).
                where(Student.tgID == userID))
        
        scalarID = session.scalar(stmt)

    if not scalarID:
        kb = InlineKeyboardBuilder()
        kb.button(text="✅", callback_data="agreement")
        start_kb = kb.as_markup()

        await message.answer('💼 <b>ДОБРО ПОЖАЛОВАТЬ!</b>\n\nВ электронный журнал "Астраханского Колледжа Вычислительной Техники"!\n\n'\
                            'Если вы готовы приступить к регистрации, нажмите на галочку.', parse_mode=ParseMode.HTML, reply_markup=start_kb)
    else:
        await message.answer("<b>❌ ОТКАЗАНО</b>\n\nВы уже <b>АВТОРИЗОВАНЫ.</b>", parse_mode=ParseMode.HTML)
       