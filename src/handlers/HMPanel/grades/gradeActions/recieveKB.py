from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.db.engine import localSession
from src.db.models import Student
from src.functions.getGroup import getGroupFunc

from sqlalchemy import select

async def usersKB(tgID):
    kb = InlineKeyboardBuilder()
    group = await getGroupFunc(tgID)
    with localSession() as session:

        stmt = (
            select(Student).
            where(Student.group_name == group)
        )

        value = session.execute(stmt)
        students = value.scalars().all()

        for student in students:
            kb.button(text=f"{student.first_name} {student.second_name}", callback_data=f"gp:{student.id}")

        kb.adjust(2, 2, repeat=True)
        keyboard = kb.as_markup()
        return keyboard