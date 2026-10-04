import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

services = [
    "حجز موعد طبي",
    "استفسار عن الخدمات",
    "التواصل مع الدعم",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(s, callback_data=f"service_{i}")]
        for i, s in enumerate(services)
    ]
    await update.message.reply_text(
        "مرحبًا بك في Medksa-Bot 🏥\nاختر الخدمة المطلوبة:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    index = int(query.data.split("_")[1])
    context.user_data["service"] = services[index]
    context.user_data["step"] = "name"
    await query.message.reply_text("يرجى كتابة الاسم:")

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    text = update.message.text

    if step == "name":
        context.user_data["name"] = text
        context.user_data["step"] = "details"
        await update.message.reply_text(
            "اكتب تفاصيل طلبك والوقت المناسب للتواصل:"
        )
    elif step == "details":
        service = context.user_data["service"]
        name = context.user_data["name"]
        user = update.effective_user

        message = (
            "📩 طلب جديد\n\n"
            f"الخدمة: {service}\n"
            f"الاسم: {name}\n"
            f"التفاصيل: {text}\n"
            f"معرّف العميل: {user.id}"
        )

        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text=message,
            )

        await update.message.reply_text(
            "✅ تم استلام طلبك، وسيتم التواصل معك."
        )
        context.user_data.clear()

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_service))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message)
    )
    app.run_polling()

if __name__ == "__main__":
    main()
