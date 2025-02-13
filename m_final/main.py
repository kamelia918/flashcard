import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler,CallbackContext
from handlers.start import start
from handlers.module import modify_module_main,handle_main_add_module
from handlers.cours import handle_add_cours_main,handle_modify_course_main
from handlers.flashcard import handler_add_flashcardupdate_main,handler_modify_flashcardupdate_main
from handlers.backBTN import back_module_button
from handlers.set_revision import handle_text_input
from handlers.utils import handle_button_click, error_handler
from handlers.set_revision_f.send_notif import check_notifications


async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # modifier le nom du module
    if "modify_module" in context.user_data:
        await modify_module_main(user_id,text,update,context)

    # Ajouter un module
    elif "add_module" in context.user_data:
        await handle_main_add_module(update,context,user_id,text)
        
    #Ajouter un cours dans un module 
    elif "current_module" in context.user_data:
        await handle_add_cours_main(user_id,text,update,context)

    # modifier le nom du cours
    elif "modify_course" in context.user_data:
        await handle_modify_course_main(update,context,user_id,text)
    
    # Ajouter a flashcard
    elif "flashcard_state" in context.user_data:
        await handler_add_flashcardupdate_main(update,context,text,user_id)
        
    # modifier flashcard
    elif "modify_flashcard" in context.user_data:
        await handler_modify_flashcardupdate_main(update,context,text)
    
    # confirmer l'heure pour la revision (set revision time ) 
    elif "waiting_for_hour" in context.user_data: 
        await handle_text_input(update,context)
    
    else:
        await update.message.reply_text("Aucun bouton n'est pressé", reply_markup=back_module_button())




def main() -> None:
    print("Starting bot...")  # Debugging log

    application = Application.builder().token("7758636605:AAE3iDboYqy-5FSH2iXwUgF4_YlvkVKpBGo").build()
    
    print("Bot initialized. Adding handlers...")  # Debugging log
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Handle modules, courses, and flashcards
    application.add_handler(CallbackQueryHandler(handle_button_click))
    

    application.add_error_handler(error_handler)
    # Démarrer la vérification des notifications en tâche de fond
    loop = asyncio.get_event_loop()
    loop.create_task(check_notifications(application))


    # Start the bot
    print("Bot is running...")
    print("All handlers added. Running polling...")  # Debugging log
    application.run_polling()

if __name__ == "__main__":
    main()