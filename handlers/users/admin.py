from aiogram.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot, dp, db
from aiogram import  types
from .echo import created_at

async def sent_admin_data_and_private_channel(datas, admin_id, channel_id, user_id, user_data):
    photos = [datas['car'], datas['payment']]
    media_group = [InputMediaPhoto(media=file_id) for file_id in photos]
    check_data = db.get_last_check_by_user(telegram_id=user_id)
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_registration_{check_data[-2]}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel_registration_{check_data[-2]}")]
    ])

    await bot.send_media_group(admin_id, media=media_group)
    await bot.send_message(admin_id, "Yangi foydalanuvchi ro'yxatga olish uchun tasdiqlashni amalga oshiring.", reply_markup=admin_keyboard)


    await bot.send_media_group(channel_id, media=media_group)
    await bot.send_message(channel_id, f"Yangi ro'yxatdan o'tgan foydalanuvchi!\n\n"
                                       f"Ism va familyasi: {user_data['full_name']}\n"
                                       f"Telefon raqam: {user_data['phone']}")



@dp.callback_query(lambda query: query.data.startswith('confirm_registration'))
async def get_check(call: types.CallbackQuery):
    user_id = call.data.split('_')[-1]
    await call.answer(cache_time=60)
    await bot.send_message(chat_id=int(user_id), text=f"✅ Sizning ro'yxatdan o'tish so'rovingiz tasdiqlandi! Linklar:\n"
                                                      f" 📝 Mijozlar: https://t.me/+kM3kSKNxQVNjYzFi\n"
                                                      f"📤 Elon Berish: https://t.me/FargonaBeshariqElonBot\n"
                                                      f"🔒 Yopiq Guruh: https://t.me/+dkyxxV7rmHozYWI6")
    db.add_payment(telegram_id=user_id, created_at=created_at)
    await call.message.answer(text="✅ Foydalanuvchi tasdiqlandi")


@dp.callback_query(lambda query: query.data.startswith('cancel_registration'))
async def get_check(call: types.CallbackQuery):
    user_id = call.data.split('_')[-1]
    await call.answer(cache_time=60)
    await bot.send_message(chat_id=int(user_id), text="❌ So'rovingiz tasdiqlanmadi! Admin bilan bog'laning: +998882042629")

    await call.message.answer(text="❌ Foydalanuvchi tasdiqlanmadi")




