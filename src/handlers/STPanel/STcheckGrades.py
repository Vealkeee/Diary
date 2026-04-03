from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram import Router, F

from sqlalchemy import select, update
from src.db.models import Group, Student
from src.db.engine import localSession
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.functions.getGroup import getGroupFunc

router = Router()

@router.callback_query(F.data == "grades_status")
async def CreateConnectionKB(call: CallbackQuery, db_pool):
    group = getGroupFunc(call.from_user.id)
    with db_pool() as db:
        stmt = (
            select()
        )