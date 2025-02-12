
import datetime
import sqlite3

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext


def get_user_revisions(user_id):
    """Récupère les modules, cours et flashcards à réviser pour un utilisateur."""
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    now_date = datetime.datetime.now().strftime("%Y-%m-%d").lstrip("0").replace("-0", "-")
    now_time = datetime.datetime.now().strftime("%H:%M").lstrip("0")

    # Sélectionner les modules à réviser pour l'utilisateur
    cursor.execute('''
        SELECT DISTINCT module_name
        FROM schedules
        WHERE user_id = ? AND revision_day <= ? AND revision_time <= ?
    ''', (user_id, now_date, now_time))

    modules = cursor.fetchall()

    user_revisions = {}

    for (module_name,) in modules:
        user_revisions[module_name] = {}

        # Récupérer les cours du module
        cursor.execute('''
            SELECT DISTINCT course_name FROM schedules
            WHERE user_id = ? AND module_name = ? 
            AND (course_name IS NOT NULL AND course_name != '')
        ''', (user_id, module_name))
        courses = cursor.fetchall()

        if courses:
            for (course_name,) in courses:
                user_revisions[module_name][course_name] = []

                # Récupérer les flashcards du cours
                cursor.execute('''
                    SELECT front FROM flashcards
                    WHERE course_id IN (
                        SELECT id FROM courses 
                        WHERE course_name = ? 
                        AND module_id IN (
                            SELECT id FROM modules WHERE module_name = ?
                        )
                    )
                ''', (course_name, module_name))
                flashcards = cursor.fetchall()

                for (flashcard_front,) in flashcards:
                    user_revisions[module_name][course_name].append(flashcard_front)
        
        else:
            # Si aucun cours spécifique n'est défini, récupérer tous les cours et flashcards du module
            cursor.execute('''
                SELECT DISTINCT course_name FROM courses
                WHERE module_id IN (SELECT id FROM modules WHERE module_name = ?)
            ''', (module_name,))
            all_courses = cursor.fetchall()

            for (course_name,) in all_courses:
                user_revisions[module_name][course_name] = []

                cursor.execute('''
                    SELECT front FROM flashcards
                    WHERE course_id IN (
                        SELECT id FROM courses WHERE course_name = ?
                    )
                ''', (course_name,))
                flashcards = cursor.fetchall()

                for (flashcard_front,) in flashcards:
                    user_revisions[module_name][course_name].append(flashcard_front)

    conn.close()
    print("user revision",user_revisions)
    return user_revisions


#b. Fonction pour afficher les modules
async def start_revision_callback(update: Update, context: CallbackContext):
    """Affiche les modules à réviser."""
    query = update.callback_query
    await query.answer()  # Accuser réception du clic

    user_id = update.effective_user.id

    user_revisions = get_user_revisions(user_id)

    if not user_revisions:
        await query.edit_message_text("Aucune révision prévue pour le moment.")
        return

    # Créer un clavier avec les modules
    keyboard = []
    for module_name in user_revisions.keys():
        keyboard.append([InlineKeyboardButton(module_name, callback_data=f"select_moduleSETREVISION_{module_name}_{user_id}")])

    # Create the reply markup
    reply_markup = InlineKeyboardMarkup(keyboard)

  
    await query.edit_message_text("📚 Choisissez un module à réviser :", reply_markup=reply_markup)

#c. Fonction pour afficher les cours d'un module
async def select_module_callback(update: Update, context: CallbackContext):
    """Affiche les cours d'un module."""
    query = update.callback_query
    await query.answer()  # Accuser réception du clic

    data = query.data.split("_")
    module_name = data[2]
    user_id = data[3]

    user_revisions = get_user_revisions(user_id)
    courses = user_revisions.get(module_name, {})

    if not courses:
        await query.edit_message_text(f"Aucun cours trouvé pour le module *{module_name}*.", parse_mode="Markdown")
        return

    # Créer un clavier avec les cours
    keyboard = []
    for course_name in courses.keys():
        keyboard.append([InlineKeyboardButton(f"📖 {course_name}", callback_data=f"start_course_revision_{course_name}_{module_name}_{user_id}")])

    # Create the reply markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    
    await query.edit_message_text(f"📖 Choisissez un cours dans *{module_name}* :", parse_mode="Markdown", reply_markup=reply_markup)

#d. Fonction pour démarrer la révision des flashcards d'un cours

async def start_course_revision(update: Update, context: CallbackContext):
    """Démarre la révision des flashcards d'un cours."""
    query = update.callback_query
    await query.answer()  # Accuser réception du clic

    data = query.data.split("_")
    print("DATTAA",data)
    course_name = data[3]
    print("cours NAMEEE",course_name)
    module_name = data[4]
    user_id = data[5]

    # Récupérer les flashcards du cours
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT front, back FROM flashcards
        WHERE course_id IN (SELECT id FROM courses WHERE course_name = ?)
    ''', (course_name,))
    
    flashcards = cursor.fetchall()
    conn.close()

    if not flashcards:
        await query.edit_message_text(f"Aucune flashcard disponible pour le cours *{course_name}*.", parse_mode="Markdown")
        return

    # Stocker les flashcards en session
    context.user_data[user_id] = {
        "flashcards": flashcards,
        "index": 0,
        "course_name": course_name,
        "module_name": module_name
    }

    # Afficher la première flashcard
    first_flashcard = flashcards[0][0]
    keyboard = []
    keyboard.append([InlineKeyboardButton("🧐 Voir la réponse", callback_data=f"show_answer_{user_id}")])

    # Create the reply markup
    reply_markup = InlineKeyboardMarkup(keyboard)


    await query.edit_message_text(f"📝 *{course_name}*\n\n🔹 {first_flashcard}", parse_mode="Markdown", reply_markup=reply_markup)


#e. Fonction pour afficher la réponse et passer à la flashcard suivante
async def show_answer_callback(update: Update, context: CallbackContext):
    """Affiche la réponse et permet de passer à la flashcard suivante."""
    query = update.callback_query
    await query.answer()  # Accuser réception du clic

    # Parse callback data
    data = query.data.split("_")
    print("DATA ???", data)
    user_id = data[2]  # Extract user ID from the callback data

    # Retrieve user data from `context.user_data`
    user_data = context.user_data.get(user_id, None)

    if not user_data or "flashcards" not in user_data or "index" not in user_data:
        await query.edit_message_text("Erreur, veuillez recommencer la révision.")
        return

    # Retrieve the current flashcard details
    index = user_data["index"]
    flashcards = user_data["flashcards"]
    front, back = flashcards[index]

    # Display the answer with options
    keyboard = [
        [InlineKeyboardButton("✅ Oui", callback_data=f"remembered_{user_id}")],
        [InlineKeyboardButton("❌ Non", callback_data=f"forgot_{user_id}")],
        [InlineKeyboardButton("➡️ Suivant", callback_data=f"next_card_setTime_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"📝 {front}\n\n🔹 *Réponse* : {back}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

#f. Fonction pour passer à la flashcard suivante
async def next_flashcard_callback(update: Update, context: CallbackContext):
    """Passe à la flashcard suivante."""
    query = update.callback_query
    await query.answer()  # Accuser réception du clic

    # Parse callback data
    user_data_parsed = query.data.split("_")
    print("DATA ???", user_data_parsed)
    if len(user_data_parsed) == 3:
        user_id = user_data_parsed[2]  # Extract user ID from callback data
    else:
        user_id = user_data_parsed[3]  # Extract user ID from callback data

    # Retrieve user data from `context.user_data`
    user_data = context.user_data.get(user_id, None)

    if not user_data or "flashcards" not in user_data or "index" not in user_data:
        await query.edit_message_text("Erreur, veuillez recommencer la révision.")
        return

    # Move to the next flashcard
    user_data["index"] += 1
    index = user_data["index"]
    flashcards = user_data["flashcards"]

    if index >= len(flashcards):
        # End of revision for this course
        await query.edit_message_text("🎉 Vous avez terminé la révision de ce cours !")

        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()
        now_date = datetime.datetime.now().strftime("%Y-%m-%d").lstrip("0").replace("-0", "-")
        now_time = datetime.datetime.now().strftime("%H:%M").lstrip("0")

        # Remove the course from the schedules table
        cursor.execute(
            '''
            DELETE FROM schedules
            WHERE user_id = ? AND module_name = ? AND course_name = ?
            ''',
            (user_id, user_data["module_name"], user_data["course_name"])
        )
        conn.commit()

        # Check if the module still has other courses to review
        cursor.execute(
            '''
            SELECT COUNT(*)
            FROM schedules
            WHERE user_id = ? AND module_name = ? AND revision_day <= ? AND revision_time <= ?
            ''',
            (user_id, user_data["module_name"],now_date,now_time)
        )
        remaining_courses = cursor.fetchone()[0]

        if remaining_courses == 0:
            # Delete the module if no other courses are due
            cursor.execute(
                '''
                DELETE FROM modules
                WHERE user_id = ? AND module_name = ?
                ''',
                (user_id, user_data["module_name"])
            )
            conn.commit()

            await query.edit_message_text(
                f"🎉 Vous avez terminé la révision de tous les cours du module *{user_data['module_name']}* !",
                parse_mode="Markdown"
            )

        conn.close()
        return

    # Display the next flashcard
    front, _ = flashcards[index]
    keyboard = [
        [InlineKeyboardButton("🧐 Voir la réponse", callback_data=f"show_answer_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"📝 *{user_data['course_name']}*\n\n🔹 {front}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

