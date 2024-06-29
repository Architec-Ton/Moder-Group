from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Настройки группы', callback_data="settings"
            ),
            InlineKeyboardButton(
                text='Наказания', callback_data='nakaz'
            )
        ]
    ]
)

