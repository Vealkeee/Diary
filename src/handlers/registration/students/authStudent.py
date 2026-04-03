from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram import Router, F

from sqlalchemy import select, update
from src.db.models import Group, Student
from src.db.engine import localSession
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

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
                await call.message.answer("<b>🎄 ПРИВЯЗКА</b>\n\nВ вашей группе отсутствует староста... Попробуйте позже.", parse_mode=ParseMode.HTML)
        elif status == True:
            await call.message.answer("<b>🎄 ПРИВЯЗКА</b>\n\nАккаунт уже <b>привязан</b> к старосте...", parse_mode=ParseMode.HTML)
        else:
            await call.message.answer("<b>🎄 ПРИВЯЗКА</b>\n\nАккаунт находится в процессе привязки...", parse_mode=ParseMode.HTML)
        
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