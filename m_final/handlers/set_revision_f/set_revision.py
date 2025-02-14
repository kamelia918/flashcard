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

async def handle_set_Time(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    user_id = update.effective_user.id


    # Create a list of buttons for each module
    keyboard = []
    
    keyboard.append([InlineKeyboardButton("📅 planning révision", callback_data=f"palnning")])
            
    keyboard.append([InlineKeyboardButton("🕗 Définir l'heure", callback_data="listModule_")])
    keyboard.append([InlineKeyboardButton("revisions ratées ", callback_data=f"start_revision_{user_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="back_to_start")])            
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Révision:", reply_markup=reply_markup)    


async def handle_planning_set_time(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Accuser réception du clic sur le bouton
    user_id = update.effective_user.id

    # Connexion à la base de données
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    try:
        # Vérifier si la colonne revision_time existe
        cursor.execute('PRAGMA table_info(schedules)')
        columns = [column[1] for column in cursor.fetchall()]
        print("columns",columns)
        if 'revision_time' not in columns:
            await query.edit_message_text("Erreur : la colonne 'revision_time' n'existe pas dans la table.")
            return

        # Récupérer tous les enregistrements de l'utilisateur dans la table schedules
        cursor.execute('''
            SELECT revision_day, revision_time, module_name, course_name, flashcard_id
            FROM schedules
            WHERE user_id = ?
            ORDER BY revision_day, revision_time
        ''', (user_id,))
        rows = cursor.fetchall()

        if not rows:
            # Aucun enregistrement trouvé
            await query.edit_message_text("Vous n'avez aucun planning enregistré.")
            return

        # Formater les données pour l'affichage
        planning_message = "📅 Votre planning :\n\n"
        current_date = None
        current_time = None

        for row in rows:
            revision_day, revision_time, module_name, course_name, flashcard_id = row

            # Afficher la date si elle change
            if revision_day != current_date:
                planning_message += f"📅 **Date : {revision_day}**\n"
                current_date = revision_day
                current_time = None

            # Afficher l'heure si elle change
            if revision_time != current_time:
                planning_message += f"⏰ **Heure : {revision_time}**\n"
                current_time = revision_time

            # Afficher les détails du module, cours et flashcard
            planning_message += f"  - Module : {module_name}\n"
            planning_message += f"  - Cours : {course_name}\n"
            planning_message += f"  - Flashcard ID : {flashcard_id}\n\n"

        # Envoyer le message à l'utilisateur
        await query.edit_message_text(planning_message, parse_mode="Markdown")

    except Exception as e:
        # Gérer les erreurs
        await query.edit_message_text(f"Une erreur s'est produite : {e}")
    finally:
        # Fermer la connexion à la base de données
        conn.close()






# 📌 Fonction pour générer le calendrier du mois
import calendar
def generate_calendar(year: int, month: int):
    today = datetime.now()  # Date actuelle
    days_in_month = calendar.monthrange(year, month)[1]
    keyboard = []

    # Générer les boutons pour chaque jour du mois
    for week in range(0, days_in_month, 7):
        row = []
        for day in range(week + 1, min(week + 8, days_in_month + 1)):
            # Désactiver les boutons des jours passés
            if (year < today.year) or (year == today.year and month < today.month) or (year == today.year and month == today.month and day < today.day):
                row.append(InlineKeyboardButton("❌", callback_data="disabled"))  # Bouton désactivé
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=f"select_day_{year}_{month}_{day}"))
        keyboard.append(row)

    # Boutons "Mois précédent" et "Mois suivant"
    prev_month_button = InlineKeyboardButton("⏪ Mois précédent", callback_data=f"prev_month_{year}_{month}")
    next_month_button = InlineKeyboardButton("⏩ Mois suivant", callback_data=f"next_month_{year}_{month}")

    # Désactiver le bouton "Mois précédent" si le mois actuel est le mois en cours
    if year == today.year and month == today.month:
        prev_month_button = InlineKeyboardButton("❌ Mois précédent", callback_data="disabled")

    keyboard.append([prev_month_button, next_month_button])
    
    return InlineKeyboardMarkup(keyboard)

# 📌 Fonction pour afficher le calendrier
async def handle_set_time_module(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    clicked_button_data = query.data

    # Extraire le module depuis callback_data
    parts = clicked_button_data.split("_")
    if len(parts) == 4:  # Format: "definir_H_module_moduleName"
        _, _, _, module_name = parts
        context.user_data['selected_module'] = module_name  # Stocker temporairement le module

        today = datetime.now()
        calendar_markup = generate_calendar(today.year, today.month)

        await query.edit_message_text("📅 Sélectionnez une date :", reply_markup=calendar_markup)

async def handle_set_time_course(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    clicked_button_data = query.data

    # Extraire le module depuis callback_data
    parts = clicked_button_data.split("_")
    print("set time cours parts ",parts)
    if len(parts) == 5:  # Format: "definir_H_module_moduleName"
        _, _, _, module_name,course_name = parts
        context.user_data['selected_module'] = module_name  # Stocker temporairement le module
        context.user_data['selected_course'] = course_name  # Stocker temporairement le cours


        today = datetime.now()
        calendar_markup = generate_calendar(today.year, today.month)

        await query.edit_message_text("📅 Sélectionnez une date :", reply_markup=calendar_markup)

async def handle_set_time_flashcard(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    clicked_button_data = query.data

    # Extraire le module depuis callback_data
    parts = clicked_button_data.split("_")
    print("parts of flashcard ",parts)
    if len(parts) == 6:  # Format: "definir_H_module_moduleName"
        _, _, _, module_name,course_name,flashcardID = parts
        context.user_data['selected_module'] = module_name  # Stocker temporairement le module
        context.user_data['selected_course'] = course_name  # Stocker temporairement le cours
        context.user_data['selected_flashcard'] = flashcardID  # Stocker temporairement la carte


        today = datetime.now()
        calendar_markup = generate_calendar(today.year, today.month)

        await query.edit_message_text("📅 Sélectionnez une date :", reply_markup=calendar_markup)


# 📌 Gestion de la sélection de l'heure

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import re

# Définir les états de la conversation
SELECT_HOUR, CONFIRM_HOUR = range(2)

async def select_day(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    if len(parts) == 5:  # Format: "select_day_year_month_day"
        _, _, year, month, day = parts
    
        selected_date = f"{int(year)}-{int(month)}-{int(day)}"
        context.user_data['selected_date'] = selected_date  # Stocker temporairement la date

        # Afficher les heures disponibles
        keyboard = []
        keyboard.append([InlineKeyboardButton("➕ Ajouter une heure", callback_data=f"add_hour_{year}_{month}_{day}")]) # calls confirm scheadule
        keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data=f"select_day_{year}_{month}_{day}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(f"📆 Date choisie : {selected_date}\n🕗 appuyer sur «Ajouter une heure» pour ajouter une heure de révision:", reply_markup=reply_markup)
        

async def add_hour(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    # Demander à l'utilisateur de saisir une heure
    await query.edit_message_text("Veuillez saisir une heure au format HH:MM (par exemple, 14:30):")
    
    # Stocker l'état actuel dans user_data
    context.user_data['waiting_for_hour'] = True

async def handle_text_input(update: Update, context: CallbackContext):
    # Vérifier si on attend une heure de l'utilisateur
    if context.user_data.get('waiting_for_hour'):
        user_input = update.message.text
        await validate_hour(update, context, user_input)
    else:
        # Gérer d'autres messages texte
        await update.message.reply_text("Je ne comprends pas cette commande.")

async def validate_hour(update: Update, context: CallbackContext, user_input: str):
    if re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', user_input):
        # Heure valide
        context.user_data['selected_hour'] = user_input
        context.user_data['waiting_for_hour'] = False  # On n'attend plus d'heure
        
        # Afficher un message avec un bouton "Confirmer"
        keyboard = [[InlineKeyboardButton("✅ Confirmer", callback_data="confirm_hour")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Vous avez choisi l'heure : {user_input} \n" "👉 Confirmez-vous cette programmation ?", reply_markup=reply_markup)
    else:
        # Heure invalide, redemander
        await update.message.reply_text("Heure incorrecte. Veuillez saisir une heure au format HH:MM (par exemple, 14:30):")
        
async def confirm_hour(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    selected_date = context.user_data.get('selected_date')
    selected_hour = context.user_data.get('selected_hour')
    
    # Sauvegarder l'heure (vous pouvez implémenter cette partie selon vos besoins)
    await save_hour(update,context)
    keyboard = []
    
    keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="listModule_")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(f"✅ Heure enregistrée : {selected_hour}\n"
                                    f"📅 Date : {selected_date}\n",reply_markup=reply_markup)
    # Bloquer le clavier pour empêcher les saisies
    await update.message.reply_text(
        "Vous ne pouvez pas saisir de texte .",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

import sqlite3

async def save_hour(update: Update, context: CallbackContext):
    # Récupérer les données de l'utilisateur
    module_name = context.user_data.get('selected_module')
    course_name = (context.user_data or {}).get('selected_course', "")
    flashcard = (context.user_data or {}).get('selected_flashcard', "")
    selected_date = context.user_data.get('selected_date')
    selected_hour = context.user_data.get('selected_hour')

    query = update.callback_query
    await query.answer()

    # Connexion à la base de données
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    try:
        # Cas 1 : Une flashcard est spécifiée
        if flashcard:
            # Vérifier si la flashcard existe déjà pour cette date
            cursor.execute('''
                SELECT id FROM schedules
                WHERE flashcard_id = ? AND revision_day = ? AND revision_time = ?
            ''', (flashcard, selected_date,selected_hour))
            existing_entry = cursor.fetchone()

            if existing_entry:
                # La flashcard existe déjà pour cette date
                await query.edit_message_text("Cette carte a déjà été sauvegardée pour cette date.")
            else:
                # Insérer la flashcard dans la table schedules
                cursor.execute('''
                    INSERT INTO schedules (user_id, module_name, course_name, flashcard_id, revision_day, revision_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (update.effective_user.id, module_name, course_name, flashcard, selected_date, selected_hour))
                conn.commit()
                await query.edit_message_text("La carte a été sauvegardée avec succès.")

        # Cas 2 : Aucune flashcard spécifiée, mais un cours est spécifié
        elif course_name:
            # Récupérer toutes les flashcards associées à ce cours
            cursor.execute('''
                SELECT id FROM flashcards
                WHERE course_id = (
                    SELECT id FROM courses
                    WHERE course_name = ? AND module_id = (
                        SELECT id FROM modules
                        WHERE module_name = ? AND user_id = ?
                    )
                )
            ''', (course_name, module_name, update.effective_user.id))
            flashcards = cursor.fetchall()

            for flashcard_id in flashcards:
                # Vérifier si la flashcard existe déjà pour cette date
                cursor.execute('''
                    SELECT id FROM schedules
                    WHERE flashcard_id = ? AND revision_day = ? AND revision_time = ?
                ''', (flashcard_id[0], selected_date,selected_hour))
                existing_entry = cursor.fetchone()

                if not existing_entry:
                    # Insérer la flashcard dans la table schedules
                    cursor.execute('''
                        INSERT INTO schedules (user_id, module_name, course_name, flashcard_id, revision_day, revision_time)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (update.effective_user.id, module_name, course_name, flashcard_id[0], selected_date, selected_hour))
                    conn.commit()

            await query.edit_message_text("Toutes les cartes du cours ont été sauvegardées avec succès.")

        # Cas 3 : Aucune flashcard ni cours spécifié, mais un module est spécifié
        elif module_name:
            # Récupérer tous les cours associés à ce module
            cursor.execute('''
                SELECT id FROM courses
                WHERE module_id = (
                    SELECT id FROM modules
                    WHERE module_name = ? AND user_id = ?
                )
            ''', (module_name, update.effective_user.id))
            courses = cursor.fetchall()

            for course_id in courses:
                # Récupérer toutes les flashcards associées à ce cours
                cursor.execute('''
                    SELECT id FROM flashcards
                    WHERE course_id = ?
                ''', (course_id[0],))
                flashcards = cursor.fetchall()

                for flashcard_id in flashcards:
                    # Vérifier si la flashcard existe déjà pour cette date
                    cursor.execute('''
                        SELECT id FROM schedules
                        WHERE flashcard_id = ? AND revision_day = ? AND revision_time = ? 
                    ''', (flashcard_id[0], selected_date,selected_hour))
                    existing_entry = cursor.fetchone()

                    if not existing_entry:
                        # Insérer la flashcard dans la table schedules
                        cursor.execute('''
                            INSERT INTO schedules (user_id, module_name, course_name, flashcard_id, revision_day, revision_time)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (update.effective_user.id, module_name, course_name, flashcard_id[0], selected_date, selected_hour))
                        conn.commit()

            await query.edit_message_text("Toutes les cartes du module ont été sauvegardées avec succès.")

        # Cas 4 : Aucune donnée valide
        else:
            await query.edit_message_text("Aucune donnée valide pour sauvegarder.")

    except Exception as e:
        # Gérer les erreurs
        await query.edit_message_text(f"Une erreur s'est produite : {e}")
    finally:
        # Fermer la connexion à la base de données
                # Exécuter une requête pour récupérer toutes les lignes de la table schedules
        cursor.execute('SELECT * FROM schedules')
        rows = cursor.fetchall()

        # Afficher les en-têtes de colonnes
        column_names = [description[0] for description in cursor.description]
        print(" | ".join(column_names))

        # Afficher les lignes de la table
        for row in rows:
            print(" | ".join(map(str, row)))

        conn.close()    


    
    



async def handle_time_input(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    print("Entering this zone")

    # Extraire year, month, et day du callback_data
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    print ("part of ",parts)
    if len(parts) == 5:  # Format: "select_day_year_month_day"
        _, _, year, month, day = parts
    
        selected_date = f"{year}-{month}-{day}"
        context.user_data['selected_date'] = selected_date  # Stocker la date sélectionnée
    
        # Vérifier si l'utilisateur a envoyé un message
        if update.message:
            user_input = update.message.text.strip()  # Récupérer la saisie de l'utilisateur
        else:
            # Si appelé explicitement, définir une valeur par défaut ou demander une saisie
            user_input = "14:30"  # Valeur par défaut (à adapter)

        # Valider le format de l'heure avec une expression régulière
        if re.match(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", user_input):
            # Si l'heure est valide, la stocker dans context.user_data
            context.user_data['selected_time'] = user_input

            # Afficher un message de confirmation
            if update.message:
                await update.message.reply_text(
                    f"✅ Heure enregistrée : {user_input}\n"
                    f"📅 Date : {selected_date}\n"
                    "👉 Confirmez-vous cette programmation ?",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ Confirmer", callback_data="confirm_schedule")]
                    ])
                )
            else:
                keyboard = []
                keyboard.append([InlineKeyboardButton("✅ Confirmer", callback_data="confirm_schedule")])
                keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data=f"select_day_{year}_{month}_{day}")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                # Use query.edit_message_text if update.message is None
                await query.edit_message_text(
                    f"✅ Heure enregistrée : {user_input}\n"
                    f"📅 Date : {selected_date}\n"
                    "👉 Confirmez-vous cette programmation ?",
                    reply_markup=reply_markup
                )
            return  # Passer à l'état suivant pour la confirmation
        else:
            # Si l'heure est invalide, demander à l'utilisateur de réessayer
            if update.message:
                await update.message.reply_text(
                    "❌ Format d'heure invalide. Veuillez saisir une heure au format **HH:MM** (par exemple, 14:30) :"
                )
            else:
                # Use context.bot.send_message if update.message is None
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ Format d'heure invalide. Veuillez saisir une heure au format **HH:MM** (par exemple, 14:30) :"
                )
            return  # Rester dans le même état pour attendre une nouvelle saisie# async def handle_time_input(txt:str,update: Update, context: CallbackContext):

async def confirm_schedule(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    clicked_button_data = query.data
    parts = clicked_button_data.split("_")
    print ("part of confirm schedule  ",parts)


    # Récupérer les informations enregistrées
    module_name = context.user_data['selected_module']
    revision_day = context.user_data['selected_date']
    revision_time = context.user_data['selected_time']
    course_name = ""
    flashcard_id = ""

    # Connexion à la base de données SQLite et stockage
    conn = sqlite3.connect("database.db")
    add_schedule(conn, user_id, module_name, course_name, flashcard_id, revision_day, revision_time)
    conn.close()

    await query.edit_message_text(f"✅ Horaire enregistré avec succès !\n📚 Module : {module_name}\n📅 Date : {revision_day}\n🕗 Heure : {revision_time}")



