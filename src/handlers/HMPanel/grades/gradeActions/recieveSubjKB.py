from aiogram.utils.keyboard import InlineKeyboardBuilder

class UpdatesToGrades:

    async def subjKB():
        kb = InlineKeyboardBuilder()
        for i in range(11):
            kb.button(text=f"{i+1}", callback_data=f"{i+1}")
        kb.button(text="💼 Предметы", callback_data="subject_list")
        kb.adjust(4, 4, 3, 1)
        keyboard = kb.as_markup()
        return keyboard
    
    async def insert():
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Заполнить оценки", callback_data="WriteGrades")
        keyboard = kb.as_markup()
        return keyboard