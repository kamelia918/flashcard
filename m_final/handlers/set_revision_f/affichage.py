from data.storage import *

from telegram.ext import CallbackContext
import datetime
import sqlite3
from data.storage import *
from telegram import ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)
import nest_asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # Import APScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

async def handle_list_modules_set_Time(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    user_id = update.effective_user.id

    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()

        # Récupérer uniquement les modules qui ont des flashcards
        cursor.execute("""
            SELECT DISTINCT m.module_name 
            FROM modules m
            JOIN courses c ON m.id = c.module_id
            JOIN flashcards f ON c.id = f.course_id
            WHERE m.user_id = ?
        """, (user_id,))
        
        modules = [row[0] for row in cursor.fetchall()]  # Extraire les noms des modules

        keyboard = []
        if modules:  # Vérifier s'il y a des modules avec des flashcards
            for module in modules:
                keyboard.append([
                    InlineKeyboardButton(module, callback_data=f"moduletime_{module}"),
                    InlineKeyboardButton("🕗 Définir l'heure", callback_data=f"definir_time_module_{module}"),
                ])
        else:
            keyboard.append([InlineKeyboardButton("➕ Ajouter une carte", callback_data="add_flashcard_")])

        keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="set_")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = "Vos modules:" if modules else "Aucune carte ajoutée pour l'instant. Cliquez sur <b>Ajouter une carte</b> pour en créer une."
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")
         

async def handle_list_cours_set_time(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    user_id = update.effective_user.id

    print("last button", context.user_data.get('initial_action'))

    # Extract module name from callback data
    parts = clicked_button_data.split("_")
    if len(parts) == 2:  # Format: "moduletime_moduleName"
        _, module_name = parts
    else:
        await query.edit_message_text("Format de données invalide pour la liste des cours.")
        return

    # Récupérer uniquement les cours qui ont des flashcards
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT c.course_name
            FROM courses c
            JOIN flashcards f ON c.id = f.course_id
            JOIN modules m ON c.module_id = m.id
            WHERE m.user_id = ? AND m.module_name = ?
        """, (user_id, module_name))

        courses = [row[0] for row in cursor.fetchall()]  # Extraire les noms des cours

    keyboard = []
    if courses:  # Vérifier s'il y a des cours avec des flashcards
        for course in courses:
            keyboard.append([
                InlineKeyboardButton(course, callback_data=f"coursetime_{module_name}_{course}"),
                InlineKeyboardButton("🕗 Définir l'heure", callback_data=f"definir_time_cours_{module_name}_{course}"),
            ])
    else:
        keyboard.append([InlineKeyboardButton("➕ Ajouter un cours", callback_data=f"add_course_{module_name}")])

    keyboard.append([InlineKeyboardButton("🔙 Retour à la liste des modules", callback_data="listModule_")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = f"Cours du module <b>'{module_name}'</b>:" if courses else f"""Aucun cours dans le module <b>{module_name}</b> ajouté pour l'instant. Cliquez sur <b>Ajouter un cours</b> pour en créer un."""
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")



async def handler_list_flashcardupdate_set_time(update : Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    user_id = update.effective_user.id
    clicked_button_data = query.data  # Get the callback_data of the clicked button
    parts = clicked_button_data.split("_")
    if len(parts) == 3:  # Format: "list_flashcards_moduleName_courseName"
        _, module_name, course_name = parts
        flashcards = get_flashcards(module_name, course_name, user_id)
        keyboard =[]
        keyboard.append([InlineKeyboardButton("Back", callback_data=f"moduletime_{module_name}")])
                
        reply_markup = InlineKeyboardMarkup(keyboard)

        if not flashcards:
            await query.edit_message_text("No flashcards found.", reply_markup=reply_markup())
        else:
            context.user_data["module_name"]=module_name
            context.user_data["course_name"]=course_name
            # Create buttons with modify/delete options
            keyboard = [
                    [
                        InlineKeyboardButton(f"{f['front']}", callback_data=f"show_flashcard_{f['id']}"),
                        InlineKeyboardButton("🕗 Définir l'heure", callback_data=f"definir_time_flashcard_{module_name}_{course_name}_{f['id']}")
                    ]
                for f in flashcards
                ]
            keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data=f"moduletime_{module_name}")])
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Flashcards:", reply_markup=reply_markup)

