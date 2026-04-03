from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

headman_main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🧮 Успеваемость", callback_data="grades_status_hd"),
            InlineKeyboardButton(text="📝 Домашняя работа", callback_data="homework_hd")
        ],
        [
            InlineKeyboardButton(text="🗓️ Расписание", callback_data="schedule_hd"),
            InlineKeyboardButton(text="✅ Привязки", callback_data="studentConnections")
        ]
    ]
)

student_main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🧮 Успеваемость", callback_data="grades_status"),
            InlineKeyboardButton(text="📝 Домашняя работа", callback_data="homework")
        ],
        [
            InlineKeyboardButton(text="🗓️ Расписание", callback_data="schedule")
        ]
    ]
)