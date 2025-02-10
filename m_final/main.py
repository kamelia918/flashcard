# #This file will initialize the bot and register all handlers.


import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler,CallbackContext
from handlers.start import start,set_commands
from handlers.module import modify_module_main
from handlers.cours import handle_add_cours_main
from handlers.backBTN import back_cours_button , back_module_button
from handlers.set_revision import *
from handlers.utils import handle_button_click, handle_revision_feedback,handle_show_back,handle_restart_revision,handle_next_card,handle_delete_module,handle_modify_module,handle_delete_course,handle_modify_course,handle_delete_flashcard,handle_modify_choice,handle_modify_flashcard , error_handler
from data.storage import add_course, add_module, add_flashcard,get_modules,get_courses,get_module_id,get_flashcards,modify_module,modify_cours,modify_flashcard

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if "modify_module" in context.user_data:
        await modify_module_main(user_id,text,update,context)
    #Ajouter un cours dans un module 
    elif "current_module" in context.user_data:
        await handle_add_cours_main(user_id,text,update,context)
        # Adding a course
        # module_name = context.user_data["current_module"]
        # print("current module",module_name)
        # module_id = get_module_id(module_name, user_id)

        # if not module_name:
        #     await update.message.reply_text(f"Module '{module_name}' not found.", reply_markup=get_back_button())
        #     return

        # # Adding a module
        # cours_name = text
        # courses = get_courses(module_name,user_id)  # Fetch all modules for the user

        # if cours_name in courses:
        #     await update.message.reply_text(f"Le cours '{cours_name}' existe déjà.", reply_markup=get_back_button())
        #     return  # Stop execution to prevent adding a duplicate module

        # result = add_course(module_id, text, user_id)
        # if result == "success":
        #     await update.message.reply_text(f"✅ Le cours <b>« {text} »</b> a été ajouté au module <b>« {module_name} »</b> !", reply_markup=get_back_button(),parse_mode="HTML")
        # elif result == "duplicate_course":
        #     await update.message.reply_text(f"Le cours '{text}' existe déjà '{module_name}'.", reply_markup=get_back_button())
        # del context.user_data["current_module"]

    elif "waiting_for_hour" in context.user_data: # confirmer l'heure pour la revision 
        await handle_text_input(update,context)
    
    elif "modify_course" in context.user_data:
        # Modify course name
        print("conetxt user data :",context.user_data)
        module_name = context.user_data["modify_course"]["module"]
        print("module name ",module_name)
        old_name = context.user_data["modify_course"]["old_name"]
        result = modify_cours(module_name, old_name, text, user_id)
        print("resultat modify cours ",result)
        if result == "success":
            await update.message.reply_text(f"Course '{old_name}' renamed to '{text}'.", reply_markup=back_cours_button())
        elif result == "duplicate_course":
            await update.message.reply_text(f"Course '{text}' already exists in module '{module_name}'.", reply_markup=back_cours_button())
        
        del context.user_data["modify_course"]

    
    elif "flashcard_state" in context.user_data:
        # Adding a flashcard
        flashcard_state = context.user_data["flashcard_state"]
        module_name = flashcard_state["module"]
        course_name = flashcard_state["course"]

        if flashcard_state["step"] == "front":
            context.user_data["flashcard_state"]["front"] = text
            # Check if the flashcard already exists
            # Check if the flashcard with the given front text already exists
            if any(flashcard['front'] == text for flashcard in get_flashcards(module_name, course_name, user_id)):
                await update.message.reply_text(f"Flashcard with front '{text}' already exists in this course.", reply_markup=back_cours_button())
                return
            context.user_data["flashcard_state"]["step"] = "back"
            await update.message.reply_text("Veuillez maintenant saisir le <b>verso</b> de la carte mémoire. 🔄", reply_markup=back_cours_button(), parse_mode="HTML")
        elif flashcard_state["step"] == "back":
            front = context.user_data["flashcard_state"]["front"]
            back = text
            
            result = add_flashcard(module_name, course_name, front, back, user_id)
            if result == "success":
                await update.message.reply_text(f"✅ Flashcard added!\n<b>Front:</b> {front}\n<b>Back:</b> {back}", reply_markup=back_cours_button(), parse_mode="HTML")
            elif result == "duplicate_flashcard":
                await update.message.reply_text(f"Flashcard with front '{front}' already exists in this course.", reply_markup=back_cours_button())
            del context.user_data["flashcard_state"]

    elif "modify_flashcard" in context.user_data:
        state = context.user_data["modify_flashcard"]
        flashcard_id = state["id"]
        choice = state.get("choice")
        
        if choice == "modify_front":
            modify_flashcard(flashcard_id, new_front=text)
            await update.message.reply_text("Front updated!", reply_markup=back_cours_button())
            del context.user_data["modify_flashcard"]
            
        elif choice == "modify_back":
            modify_flashcard(flashcard_id, new_back=text)
            await update.message.reply_text("Back updated!", reply_markup=back_cours_button())
            del context.user_data["modify_flashcard"]
            
        elif choice == "modify_both":
            if "new_front" not in state:
                state["new_front"] = text
                await update.message.reply_text("Now enter the new BACK text:")
            else:
                modify_flashcard(flashcard_id, new_front=state["new_front"], new_back=text)
                await update.message.reply_text("Front and back updated!", reply_markup=back_cours_button())
                del context.user_data["modify_flashcard"]

    else:
        # Adding a module
        module_name = text
        modules = get_modules(user_id)  # Fetch all modules for the user

        if module_name in modules:
            await update.message.reply_text(f"Module '{module_name}' already exists.", reply_markup=back_module_button())
            return  # Stop execution to prevent adding a duplicate module

        result = add_module(module_name, user_id)

        if result == "success":
            await update.message.reply_text(f"Module '{module_name}' added!", reply_markup=back_module_button())
        elif result == "duplicate_module":
            await update.message.reply_text(f"Module '{module_name}' already exists.", reply_markup=back_module_button())





import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

# Connexion à la base de données
def get_db_connection():
    return sqlite3.connect('bot_data.db')

# Fonction pour planifier les alertes
def schedule_alerts(application: Application):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer toutes les révisions futures
    cursor.execute('''
        SELECT user_id, revision_day, revision_time, module_name, course_name
        FROM schedules
        WHERE revision_day >= DATE('now')
    ''')
    rows = cursor.fetchall()

    # Planifier une alerte pour chaque révision
    for row in rows:
        user_id, revision_day, revision_time, module_name, course_name = row
        revision_datetime = datetime.strptime(f"{revision_day} {revision_time}", "%Y-%m-%d %H:%M")

        # Planifier la tâche
        application.job_queue.run_once(
            send_reminder,
            revision_datetime,
            data=(user_id, module_name, course_name),
            name=f"reminder_{user_id}_{revision_day}_{revision_time}"
        )

    conn.close()

# Fonction pour envoyer une notification
async def send_reminder(context: CallbackContext):
    user_id, module_name, course_name = context.job.data

    # Envoyer un message à l'utilisateur
    await context.bot.send_message(
        chat_id=user_id,
        text=f"⏰ Il est l'heure de réviser !\n\nModule : {module_name}\nCours : {course_name}"
    )


def main() -> None:
    print("Starting bot...")  # Debugging log

    application = Application.builder().token("7758636605:AAE3iDboYqy-5FSH2iXwUgF4_YlvkVKpBGo").build()
    
    print("Bot initialized. Adding handlers...")  # Debugging log
    # bot = application.bot
    # await set_commands(bot)

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Handle modules, courses, and flashcards
    application.add_handler(CallbackQueryHandler(handle_button_click))
    
    # application.add_handler(CallbackQueryHandler(handle_reveal_answer, pattern="^reveal_answer_"))  # Handle reveal answer
    # application.add_handler(CallbackQueryHandler(handle_revision_feedback, pattern="^(remembered|forgot)_"))  # Handle revision feedback
    # application.add_handler(CallbackQueryHandler(handle_show_back, pattern="^show_back_"))
    # application.add_handler(CallbackQueryHandler(handle_next_card, pattern="^next_card_"))
    # application.add_handler(CallbackQueryHandler(handle_restart_revision, pattern="^restart_revision$"))
    # application.add_handler(CallbackQueryHandler(handle_modify_module, pattern="^modify_module_"))
    # application.add_handler(CallbackQueryHandler(handle_delete_module, pattern="^delete_module_"))
    # application.add_handler(CallbackQueryHandler(handle_modify_course, pattern="^modify_course_"))
    # application.add_handler(CallbackQueryHandler(handle_delete_course, pattern="^delete_course_"))
    # application.add_handler(CallbackQueryHandler(handle_delete_flashcard, pattern="^delete_flashcard_"))
    # application.add_handler(CallbackQueryHandler(handle_modify_flashcard, pattern="^modify_flashcard_"))
    # application.add_handler(CallbackQueryHandler(handle_modify_choice, pattern="^modify_(front|back|both)$"))
    # application.add_handler(CommandHandler("list_schedules", list_schedules))
    # application.add_handler(CommandHandler("delete_schedule", handle_delete_schedule))
    # # Callback query handlers
    # application.add_handler(CallbackQueryHandler(handle_set_revise_hour, pattern="^set_revise_hour$"))
    # application.add_handler(CallbackQueryHandler(handle_select_course_for_time, pattern="^select_course_for_time_"))
    # application.add_handler(CallbackQueryHandler(handle_select_flashcard_for_time, pattern="^select_flashcard_for_time_"))
    # application.add_handler(CallbackQueryHandler(handle_set_time_module, pattern="^set_time_module_"))
    # application.add_handler(CallbackQueryHandler(handle_set_time_course, pattern="^set_time_course_"))
    # application.add_handler(CallbackQueryHandler(handle_set_time_flashcard, pattern="^set_time_flashcard_"))
    # application.add_handler(CallbackQueryHandler(handle_set_day, pattern="^set_day_"))
    # application.add_handler(CallbackQueryHandler(handle_set_hour, pattern="^set_hour_"))
    # application.add_handler(CallbackQueryHandler(handle_set_minute, pattern="^set_minute_"))
    # application.add_handler(CallbackQueryHandler(process_delete_schedule, pattern="^delete_schedule_"))
    # Error handler
    schedule_alerts(application)
    application.add_error_handler(error_handler)

    # Start the bot
    print("Bot is running...")
    print("All handlers added. Running polling...")  # Debugging log
    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())