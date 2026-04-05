from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from src.handlers.HMPanel.grades.gradeActions.recieveKB import usersKB
from src.handlers.HMPanel.grades.gradeActions.recieveSubjKB import UpdatesToGrades

from src.db.models import Grade

from sqlalchemy import select

router = Router()

subjects_dict = {
    "математика": "1",
    "биология": "2",
    "русский язык": "3",
    "информатика": "4",
    "физика": "5",
    "литература": "6",
    "история": "7",
    "английский язык": "8",
    "физическая культура": "9",
    "обществознание": "10",
    "ОПД": "11"
}

class Form(StatesGroup):
    user_id = State()

@router.callback_query(F.data == "grades_status_hd")
async def UpdateSG_keyboard(call: CallbackQuery):
    await call.answer()
    keyboard = await usersKB(call.from_user.id)
    await call.message.answer(f"<b>🧮 УСПЕВАЕМОСТЬ</b>\n\nВыберите студента для изменения успеваемости.", reply_markup=keyboard, parse_mode=ParseMode.HTML)

@router.callback_query(F.data.contains("gp:"))
async def UpdateSG(call: CallbackQuery, state: FSMContext, db_pool):
    await call.answer()
    
    user_id = int(call.data.split(":")[1])
    await state.set_state(Form.user_id)
    await state.update_data(userID=user_id)

    
    keyboardToAdd = await UpdatesToGrades.subjKB()
    keyboardToInsert = await UpdatesToGrades.insert()

    with db_pool() as db:
        stmt = (
            select(Grade.id).
            where(Grade.id == user_id)
        )
        
        value = db.scalar(stmt)

        if not value:
             await call.message.answer("<b>🧮 УСПЕВАЕМОСТЬ</b>\n\nГотовы заполнить оценки пользователя?", reply_markup=keyboardToInsert, parse_mode=ParseMode.HTML)
        else:
            await call.message.answer("<b>🧮 УСПЕВАЕМОСТЬ</b>\n\nВыберите число соответствующие предмету, из списка предметов.", parse_mode=ParseMode.HTML, reply_markup=keyboardToAdd)
    
@router.callback_query(F.data.in_(subjects_dict.values()))
async def setGrade(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    userID = data.get("userID")
    await call.message.answer(f"passed: {userID}")

@router.callback_query(F.data == "subject_list")
async def UpdateSG(call: CallbackQuery):
    await call.answer(text="1. Математика\n2. Биология\n3. Русский язык\n" \
                           "4. Информатика\n5. Физика\n6. Литература\n" \
                           "7. История\n8. Английский язык\n9. Физ-ра\n" \
                           "10. Обществознание\n11. ОПД\n\n", show_alert=True)