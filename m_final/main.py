import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from handlers.start import start
from handlers.module import modify_module_main, handle_main_add_module
from handlers.cours import handle_add_cours_main, handle_modify_course_main
from handlers.flashcard import handler_add_flashcardupdate_main, handler_modify_flashcardupdate_main
from handlers.backBTN import back_module_button
from handlers.set_revision import handle_text_input
from handlers.utils import handle_button_click, error_handler, handle_photo
from handlers.set_revision_f.send_notif import check_notifications

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Modifier le nom du module
    if "modify_module" in context.user_data:
        await modify_module_main(user_id, text, update, context)

    # Ajouter un module
    elif "add_module" in context.user_data:
        await handle_main_add_module(update, context, user_id, text)

    # Ajouter un cours dans un module
    elif "current_module" in context.user_data:
        await handle_add_cours_main(user_id, text, update, context)

    # Modifier le nom du cours
    elif "modify_course" in context.user_data:
        await handle_modify_course_main(update, context, user_id, text)

    # Ajouter une flashcard
    elif "flashcard_state" in context.user_data:
        await handler_add_flashcardupdate_main(update, context, text, user_id)

    # Modifier flashcard
    elif "modify_flashcard" in context.user_data:
        await handler_modify_flashcardupdate_main(update, context, text)

    # Confirmer l'heure pour la révision (set revision time)
    elif "waiting_for_hour" in context.user_data:
        await handle_text_input(update, context)

    else:
        await update.message.reply_text("Aucun bouton n'est pressé", reply_markup=back_module_button())

def main() -> None:
    print("Starting bot...")

    application = Application.builder().token("8153876105:AAGOu0x3NR--_9G4uhbeN6B8FUdbesjmCUM").build()

    print("Bot initialized. Adding handlers...")

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))
    application.add_handler(CallbackQueryHandler(handle_button_click))
    application.add_error_handler(error_handler)

    # Démarrer la vérification des notifications en tâche de fond
    loop = asyncio.get_event_loop()
    loop.create_task(check_notifications(application))

    # Start the bot
    print("Bot is running...")
    print("All handlers added. Running polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
