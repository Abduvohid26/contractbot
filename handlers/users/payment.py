from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import pytz  # Tashkent vaqti uchun
from loader import bot, dp, db
from aiogram.types.input_file import FSInputFile
from data.config import ADMINS, CHECK_ADMIN, CHANNEL
# Tashkent vaqt zonasi
TASHKENT_TZ = pytz.timezone('Asia/Tashkent')


async def check_payment_reminders():
    today = datetime.now(TASHKENT_TZ).date()
    payments = db.all_payments()

    for user in payments:
        payment_date_str = user[-1]
        if payment_date_str is None:
            continue
        try:
            payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d").date()
            next_payment_date = payment_date + timedelta(days=30)
            days_left = (next_payment_date - today).days

            if days_left == 3:
                await send_reminder(user[-2], days_left)
            elif days_left == 2:
                await send_reminder(user[-2], days_left)
            elif days_left == 1:
                await send_reminder(user[-2], days_left)
            elif days_left == 0 or days_left < 0:
                await send_reminder(user[-2], days_left=days_left)
        except Exception as e:
            print(f"Error processing payment date for user {user[-2]}: {e}")

async def send_reminder(user_id: int, days_left: int):
    if days_left < 0:
        message = f"❌ To'lov muddatiga {days_left} kun o'tib ketti. Iltimos, to'lovni amalga oshiring."
    else:
        message = f"⚠️ To'lov muddatiga {days_left} kun qoldi. Iltimos, to'lovni amalga oshiring."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="To'lov qilish", callback_data="make_payment")]
    ])
    await bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard)
from states.state import CheckPyment
# To'lov tugmasi uchun handler
@dp.callback_query(F.data == "make_payment")
async def handle_payment_button(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    photo = FSInputFile(path='media/card.png')
    await call.message.answer_photo(photo,
                                    caption="💳 Iltimos, ushbu kartaga to‘lov qiling va to‘lov chekini rasm sifatida yuboring.")
    await state.set_state(CheckPyment.start)  # To'lovni boshlash holatini saqlash


@dp.message(CheckPyment.start)
async def get_photo(message: types.Message, state: FSMContext):
    if message.photo:
        photo_id = message.photo[-1].file_id
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_check_{message.chat.id}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel_check_{message.chat.id}")]
        ])

        # Admin paneliga yuborish
        await bot.send_photo(chat_id=int(CHECK_ADMIN), caption="💳 Tolovni tastiqlang",
                             reply_markup=admin_keyboard, photo=photo_id)

        # Admin uchun rasm yuborish
        await bot.send_photo(chat_id=int(CHECK_ADMIN),
                             caption="💳 Yangi Tolov", photo=photo_id)
        await message.answer(text="⌚️ Admin tastiqlash uchun yuborildi kuting")
        await state.clear()  # Agar boshqa holatga o'tish kerak bo'lsa

        return
    await message.answer(text="⚠️ Iltimos, to‘lov chekini rasm sifatida yuboring!")
