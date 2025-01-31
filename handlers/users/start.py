from aiogram.filters import CommandStart, StateFilter
from loader import dp, db
from aiogram import types, html, F
from states.state import RegisterState
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message
import re
from .payment import check_payment_reminders
from keyboards.inline.button import starts_bot
from datetime import datetime, timedelta
import pytz
TASHKENT_TZ = pytz.timezone('Asia/Tashkent')
today = datetime.now(TASHKENT_TZ).date()


@dp.message(CommandStart())
async def start_bot(message: types.Message, state: FSMContext):
    data = db.get_user_payments(telegram_id=message.from_user.id)
    if data:
        payment_date = datetime.strptime(data[-1], "%Y-%m-%d").date()
        next_days = payment_date + timedelta(days=30)
        left_days = (next_days - today).days
        if left_days >= 4:
            await message.answer(text=f"👤 Sida faol shartnoma mavjud qolgan kunlar {left_days}")
            return
        await check_payment_reminders()
        return
    if db.select_user(telegram_id=message.chat.id):
        await message.answer(
            html.bold(f"Assalomu alaykum, {html.link(message.from_user.full_name, f'tg://user?id={message.from_user.id}')}  🚕  Xamkor Botimizga xush kelibsiz !!!"), reply_markup=starts_bot())
        return
    db.add_user(fullname=message.from_user.full_name, telegram_id=message.from_user.id, language=message.from_user.language_code)
    await message.answer(
            html.bold(f"Assalomu alaykum, {html.link(message.from_user.full_name, f'tg://user?id={message.from_user.id}')}  🚕  Xamkor Botimizga xush kelibsiz !!!"), reply_markup=starts_bot())


@dp.message(F.text == '📏🤝 Shartnoma qilish')
async def start_bot_register(message: types.Message, state: FSMContext):
    data =  db.get_user_payments(telegram_id=message.from_user.id)
    if data:
        payment_date = datetime.strptime(data[-1], "%Y-%m-%d").date()
        next_days = payment_date + timedelta(days=30)
        left_days = (next_days-today).days
        await message.answer(text=f"👤 Sida faol shartnoma mavjud qolgan kunlar {left_days}")
        return
    await message.answer(text="📄 Ism va Familyangizni kiriting:")
    await state.set_state(RegisterState.full_name)


# --- Full Name ---
@dp.message(StateFilter(RegisterState.full_name))
async def get_full_name(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(full_name=message.text)
        await message.answer("📞 Telefon raqamingizni kiriting:")
        await state.set_state(RegisterState.phone)
        return
    await message.answer("⚠️ Iltimos, Ism va Familyangizni kiriting: ")


# --- Phone Number ---
@dp.message(StateFilter(RegisterState.phone))
async def get_phone(message: Message, state: FSMContext):
    if message.text:
        phone_pattern = r'^\+998\d{9}$'
        if re.fullmatch(phone_pattern, message.text):
            await state.update_data(phone=message.text)
            await message.answer("📸 Mashinangiz old tomonidan rasm yuboring:")
            await state.set_state(RegisterState.car)
        else:
            await message.answer("❌ Telefon raqamni to‘g‘ri formatda kiriting! (masalan: +998901234567)")
        return
    await message.answer("⚠️ Iltimos, Telfon raqamingizni kiriting: ")



from aiogram.types.input_file import FSInputFile
# --- Car Image ---
@dp.message(StateFilter(RegisterState.car))
async def get_car(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(car=message.photo[-1].file_id)
        payment_photo = FSInputFile(path='media/card.png')
        await message.answer_photo(payment_photo,
                                   caption="💳 Iltimos, ushbu kartaga to‘lov qiling va to‘lov chekini rasm sifatida yuboring.")
        await state.set_state(RegisterState.payment)
        return
    await message.answer("⚠️ Iltimos, Mashina rasmini  yuboring!")

from .admin import sent_admin_data_and_private_channel
from data.config import CHANNEL, CHECK_ADMIN
import random
# --- Payment Confirmation (Rasm ko‘rinishida) ---
@dp.message(StateFilter(RegisterState.payment))
async def confirm_payment(message: Message, state: FSMContext):
    if message.photo:

        await state.update_data(payment=message.photo[-1].file_id)

        data = await state.get_data()

        summary = (
            f"✅ Ro‘yxatdan o‘tish yakunlandi!\n\n"
            f"👤 Ism: {data['full_name']}\n"
            f"📞 Telefon: {data['phone']}\n"
            f"🚗 Mashina rasmi: ✅\n"
            f"💳 To‘lov: ✅\n\n"
            f"⌚️ To'lov tastiqlanishi bilan sizga linklar yuboriladi ⌚️"
        )
        user_data = {'full_name': data['full_name'], 'phone': data['phone']}
        await message.answer(summary, reply_markup=ReplyKeyboardRemove())
        check_id = random.randint(1, 100000000)
        db.add_check(telegram_id=message.chat.id, check_id=check_id)
        await sent_admin_data_and_private_channel(datas=data, user_id=message.chat.id, admin_id=int(CHECK_ADMIN),
                                                  channel_id=CHANNEL[0], user_data=user_data)
        await state.clear()

        return
    await message.answer("⚠️ Iltimos, to‘lov chekini rasm sifatida yuboring!")
