from loader import dp
from aiogram import types,F
@dp.message(F.text)
async def echo_bot(message:types.Message):
    await message.answer(message.text)


import pytz
from datetime import datetime

# Tashkent vaqt zonasi
tashkent_tz = pytz.timezone('Asia/Tashkent')

# Hozirgi vaqtni Tashkent vaqt zonasiga moslab olish
tashkent_time = datetime.now(tashkent_tz)

# Yaratilgan vaqtni YYYY-MM-DD formatida olish
created_at = tashkent_time.strftime('%Y-%m-%d')

