from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from sqlalchemy import select
from src.db.models import Student

from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.keyboards import student_main, headman_main
from src.functions.compare import compareFunc

from aiogram import Router, F
from redis import Redis

router = Router()
redis = Redis(host="localhost", port="6379", decode_responses=True)

@router.message(CommandStart())
async def welcome(message: Message, db_pool):

    userID = message.from_user.id
    
    with db_pool() as session:

        userID = message.from_user.id

        stmt1 = (
            select(Student.connected).
            where(Student.tgID == userID)
        )

        result = session.execute(stmt1).first()
        admin = await compareFunc(userID)

        if admin:
            await message.answer("🎓 <b>Главное меню</b>\n\nЗдесь вы можете посмотреть оценки, домашнее задание и расписание.\n\nА также, внести изменения в данные категории как староста.", parse_mode=ParseMode.HTML, reply_markup=headman_main)
        else:
            if not result:
                kb = InlineKeyboardBuilder()
                kb.button(text="✅", callback_data="agreement")
                start_kb = kb.as_markup()

                redis.set("attempt", 0, ex=120)

                await message.answer('💼 <b>ДОБРО ПОЖАЛОВАТЬ!</b>\n\nВ электронный журнал "Астраханского Колледжа Вычислительной Техники"!\n\n'\
                                        'Если вы готовы приступить к регистрации, нажмите на галочку.', parse_mode=ParseMode.HTML, reply_markup=start_kb)
            if result:

                connected = session.scalar(stmt1)

                if connected == True:
                    await message.answer("🎓 <b>Главное меню</b>\n\nЗдесь вы можете посмотреть оценки, домашнее задание и расписание.", reply_markup=student_main, parse_mode=ParseMode.HTML)
                else:
                    await message.answer("<b>❌ ОТКАЗАНО</b>\n\nВы уже <b>АВТОРИЗОВАНЫ.\n\nНо вам требуется привезать аккаунт к старосте.</b>", parse_mode=ParseMode.HTML)
                    