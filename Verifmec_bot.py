import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- CONFIG ---
BOT_TOKEN = "8302430642:AAF4w1T1stn0wt2oFm7wf_3yLH1y1D6bQyA"
REVIEW_CHAT_ID = -1002702369546  # canal de vérification
GROUPS = {
    "Groupe 1": -1001234567890,
    "Groupe 2": -1009876543210,
    "Groupe 3": -1001111111111,
    "Groupe 4": -1002222222222,
}
# --------------

logging.basicConfig(level=logging.INFO)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salut ! Envoie-moi ton âge pour commencer.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {"age": update.message.text}
        await update.message.reply_text("Merci 🙏 Maintenant envoie-moi une photo.")
    elif "photo" not in user_data[user_id]:
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            user_data[user_id]["photo"] = file_id

            keyboard = [[InlineKeyboardButton(g, callback_data=f"{user_id}:{gid}")]
                        for g, gid in GROUPS.items()]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                REVIEW_CHAT_ID,
                f"👤 Nouvelle demande :\n"
                f"👶 Âge : {user_data[user_id]['age']}\n"
                f"📸 Photo jointe",
                reply_markup=reply_markup
            )
            await context.bot.send_photo(REVIEW_CHAT_ID, file_id)
            await update.message.reply_text("✅ Merci ! Ta demande est en attente de validation.")
        else:
            await update.message.reply_text("⚠️ Merci d'envoyer une photo.")
    else:
        await update.message.reply_text("✅ Tu as déjà envoyé tes infos.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id, group_id = query.data.split(":")
    group_id = int(group_id)
    file_id = user_data[int(user_id)]["photo"]

    await context.bot.send_message(group_id, f"👤 Nouveau membre validé ! Âge : {user_data[int(user_id)]['age']}")
    await context.bot.send_photo(group_id, file_id)

    await query.edit_message_text("✅ Utilisateur ajouté au groupe choisi.")

# Debug mode pour récupérer les IDs
async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(f"📡 Debug:\nChat title: {chat.title}\nChat ID: {chat.id}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.ALL, debug))  # Debug
    app.run_polling()

if __name__ == "__main__":
    main()
