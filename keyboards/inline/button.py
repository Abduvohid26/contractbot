from aiogram.utils.keyboard import ReplyKeyboardBuilder


def starts_bot():
    btn = ReplyKeyboardBuilder()
    btn.button(text="📏🤝 Shartnoma qilish")
    return btn.as_markup(resize_keyboard=True, one_time_keyboard=True)