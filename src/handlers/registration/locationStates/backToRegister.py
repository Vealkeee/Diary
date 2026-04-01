from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, F

router = Router()

class Schema(StatesGroup):
    first_name = State()
    second_name = State()

@router.callback_query(F.data == "back1")
async def backToOne(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Schema.first_name)
    await call.message.answer("<b>✨ ИМЯ СТУДЕНТА</b>\n\nПожалуйста введите своё настоящее имя.", parse_mode=ParseMode.HTML)

@router.callback_query(F.data == "back2")
async def backToOne(message: Message, state: FSMContext):
    await state.set_state(Schema.second_name)
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Вернуться", callback_data="back1")
    keyboard = kb.as_markup()
    await message.answer("<b>✨ ФАМИЛИЯ СТУДЕНТА</b>\n\nПожалуйста введите свою настоящую фамилию.", parse_mode=ParseMode.HTML, reply_markup=keyboard)