from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, F

from src.db.models import Group
from sqlalchemy import select

router = Router()

@router.callback_query(F.data == "headman")
async def createHeadman(call: CallbackQuery, db_pool):
    with db_pool() as db:
        stmt1 = (
            select(Group.tg)
        )