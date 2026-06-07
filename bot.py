from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from datetime import datetime
import os

TOKEN = "8625749011:AAHY10HTQ0wA0gGXJHI2sVVf1KsNIUF2i1sRQ"
ADMIN_ID = 8555892705

LANGUAGE, NAME, USERNAME, PHOTO = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🇷🇺 Русский")],
        [KeyboardButton("🇬🇧 English")],
        [KeyboardButton("🇪🇸 Español")]
    ]
    await update.message.reply_text("👋 Choose your language:", 
                                  reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return LANGUAGE

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Рус" in text:
        context.user_data['lang'] = 'ru'
        await update.message.reply_text("✅ Будем общаться на русском.")
        await update.message.reply_text("Как тебя зовут или ник?")
    elif "English" in text or "Eng" in text:
        context.user_data['lang'] = 'en'
        await update.message.reply_text("✅ We'll speak in English.")
        await update.message.reply_text("What's your name or nickname?")
    else:
        context.user_data['lang'] = 'es'
        await update.message.reply_text("✅ Hablaremos en Español.")
        await update.message.reply_text("¿Cómo te llamas o cuál es tu nick?")
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    lang = context.user_data.get('lang', 'ru')
    if lang == 'ru':
        await update.message.reply_text("Твой @username в Telegram?")
    elif lang == 'en':
        await update.message.reply_text("Your Telegram @username?")
    else:
        await update.message.reply_text("Tu @username en Telegram?")
    return USERNAME

async def username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    lang = context.user_data.get('lang', 'ru')
    if lang == 'ru':
        text = "Пришли свои фото (можно несколько). Когда закончишь — напиши /done"
    elif lang == 'en':
        text = "Send your photos (you can send several). When finished — write /done"
    else:
        text = "Envía tus fotos (puedes enviar varias). Cuando termines — escribe /done"
    await update.message.reply_text(text)
    return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        file_path = f"photo_{update.effective_user.id}_{datetime.now().strftime('%H%M')}.jpg"
        await file.download_to_drive(file_path)
        context.user_data.setdefault('photos', []).append(file_path)
        
        lang = context.user_data.get('lang', 'ru')
        if lang == 'en':
            await update.message.reply_text("✅ Photo saved. Send more or write /done")
        elif lang == 'es':
            await update.message.reply_text("✅ Foto guardada. Envía más o escribe /done")
        else:
            await update.message.reply_text("✅ Фото сохранено. Ещё или /done")
    return PHOTO

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get('lang', 'ru')
    
    if lang == 'en':
        await update.message.reply_text("✅ Thank you! Application submitted.\nWe will contact you soon.")
    elif lang == 'es':
        await update.message.reply_text("✅ ¡Gracias! Solicitud enviada.\nNos pondremos en contacto pronto.")
    else:
        await update.message.reply_text("✅ Спасибо! Заявка отправлена.")

    try:
        name = user_data.get('name', 'Не указано')
        username = user_data.get('username', 'Не указано')
        photos = user_data.get('photos', [])
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔥 **НОВАЯ ЗАЯВКА!**\n\n"
                 f"👤 Имя: {name}\n"
                 f"🔗 Username: {username}\n"
                 f"📸 Фото: {len(photos)} шт."
        )
        
        for photo_path in photos:
            if os.path.exists(photo_path):
                await context.bot.send_document(chat_id=ADMIN_ID, document=open(photo_path, 'rb'))
    except:
        pass

    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username)],
            PHOTO: [
                MessageHandler(filters.PHOTO, photo),
                CommandHandler('done', done)
            ]
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
