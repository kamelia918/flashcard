import asyncio
import sqlite3
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def check_notifications(application):
    print("Testing notifications...")
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()

    try:
        while True:
            print("Checking for notifications...")
            now_date = datetime.datetime.now().strftime("%Y-%m-%d").lstrip("0").replace("-0", "-")
            now_time = datetime.datetime.now().strftime("%H:%M").lstrip("0")

            # Sélectionner tous les modules à réviser à cette heure pour chaque utilisateur
            cursor.execute('''
                SELECT DISTINCT user_id, module_name
                FROM schedules
                WHERE revision_day = ? AND revision_time = ?
            ''', (now_date, now_time))
            
            user_modules = cursor.fetchall()

            # Regrouper les révisions par utilisateur
            user_revisions = {}

            for user_id, module_name in user_modules:
                if user_id not in user_revisions:
                    user_revisions[user_id] = []
                
                user_revisions[user_id].append(module_name)

            # Envoyer un message unique par utilisateur
            for user_id, modules in user_revisions.items():
                message = "⏰ *C'est l'heure de la révision !*\n"
                message += "Vous devez réviser :\n\n"

                for module_name in modules:
                    message += f"- *{module_name}*\n"

                    # Récupérer les cours du module
                    cursor.execute('''
                        SELECT DISTINCT course_name FROM schedules
                        WHERE user_id = ? AND module_name = ? 
                        AND (course_name IS NOT NULL AND course_name != '')
                    ''', (user_id, module_name))
                    courses = cursor.fetchall()

                    if courses:
                        for (course_name,) in courses:
                            message += f"   - *{course_name}*\n"

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
                                message += f"      - {flashcard_front}\n"
                    
                    else:
                        # Si aucun cours spécifique n'est défini, récupérer tous les cours et flashcards du module
                        cursor.execute('''
                            SELECT DISTINCT course_name FROM courses
                            WHERE module_id IN (SELECT id FROM modules WHERE module_name = ?)
                        ''', (module_name,))
                        all_courses = cursor.fetchall()

                        for (course_name,) in all_courses:
                            message += f"   - *{course_name}*\n"

                            cursor.execute('''
                                SELECT front FROM flashcards
                                WHERE course_id IN (
                                    SELECT id FROM courses WHERE course_name = ?
                                )
                            ''', (course_name,))
                            flashcards = cursor.fetchall()

                            for (flashcard_front,) in flashcards:
                                message += f"      - {flashcard_front}\n"

                # Envoyer le message unique
                try:
                  
                  # Créer le clavier inline
                    keyboard = []
                    keyboard.append([InlineKeyboardButton("📖 Commencer la révision", callback_data=f"start_revision_{user_id}")])

    # Create the reply markup
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    # Envoyer le message avec le clavier
                    await application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="Markdown",
                        reply_markup=reply_markup  # Ajouter le clavier ici
                    )                

                except Exception as e:
                    print(f"Erreur lors de l'envoi du message à {user_id} : {e}")

            await asyncio.sleep(60)

    except Exception as e:
        print(f"Erreur dans la boucle de vérification des notifications : {e}")
    finally:
        conn.close()


