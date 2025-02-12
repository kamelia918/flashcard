import sqlite3
from datetime import datetime, timedelta
import os

def create_db():
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_name TEXT NOT NULL,
            UNIQUE(user_id, module_name)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            course_name TEXT NOT NULL,
            UNIQUE(module_id, course_name),
            FOREIGN KEY (module_id) REFERENCES modules(id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            next_review DATETIME,
            interval INTEGER DEFAULT 1,
            photo_path TEXT,
            UNIQUE(course_id, front),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_name TEXT,
            course_name TEXT,
            flashcard_id INTEGER,
            revision_day DATE,
            revision_time TIME,
            FOREIGN KEY (flashcard_id) REFERENCES flashcards(id)
        )
        ''')
        conn.commit()

def update_database():
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
            ALTER TABLE flashcards ADD COLUMN photo_path TEXT;
            ''')
            conn.commit()
            print("Column 'photo_path' added successfully.")
        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
            # Si la colonne existe déjà, on peut ignorer l'erreur

create_db()
update_database()
print("Database and tables created successfully.")

def add_module(module_name: str, user_id: int) -> str:
    try:
        with sqlite3.connect("bot_data.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO modules (user_id, module_name) VALUES (?, ?)",
                (user_id, module_name)
            )
            conn.commit()
            return "success"
    except sqlite3.IntegrityError:
        return "duplicate_module"

def get_modules(user_id: int) -> list:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT module_name FROM modules WHERE user_id = ?", (user_id,))
        modules = [row[0] for row in cursor.fetchall()]
    return modules

def get_module_id(module_name: str, user_id: int) -> int:
    try:
        with sqlite3.connect("bot_data.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM modules WHERE module_name = ? AND user_id = ?",
                (module_name, user_id)
            )
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    except Exception as e:
        print(f"Error occurred while retrieving module_id: {e}")
        return None

def modify_module(old_name: str, new_name: str, user_id: int) -> str:
    try:
        with sqlite3.connect("bot_data.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE modules SET module_name = ? WHERE module_name = ? AND user_id = ?",
                (new_name, old_name, user_id)
            )
            conn.commit()
            return "success"
    except sqlite3.IntegrityError:
        return "duplicate_module"

def delete_module(module_name: str, user_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM modules WHERE module_name = ? AND user_id = ?", (module_name, user_id))
        module_id = cursor.fetchone()
        if module_id:
            cursor.execute("""
                DELETE FROM flashcards
                WHERE course_id IN (
                    SELECT id FROM courses WHERE module_id = ?
                )
            """, (module_id[0],))
            cursor.execute("DELETE FROM courses WHERE module_id = ?", (module_id[0],))
            cursor.execute("DELETE FROM modules WHERE id = ?", (module_id[0],))
            conn.commit()

def add_course(module_id: int, course_name: str, user_id: int) -> str:
    try:
        with sqlite3.connect("bot_data.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO courses (module_id, course_name) VALUES (?, ?)",
                (module_id, course_name)
            )
            conn.commit()
            return "success"
    except sqlite3.IntegrityError:
        return "duplicate_course"

def get_courses(module_name: str, user_id: int) -> list:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT course_name FROM courses
            WHERE module_id = (SELECT id FROM modules WHERE module_name = ? AND user_id = ?)
        """, (module_name, user_id))
        courses = [row[0] for row in cursor.fetchall()]
    return courses

def modify_cours(module_name: str, old_name: str, new_name: str, user_id: int) -> str:
    try:
        with sqlite3.connect("bot_data.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM modules WHERE module_name = ? AND user_id = ?", (module_name, user_id))
            module_id = cursor.fetchone()
            if module_id:
                cursor.execute(
                    "UPDATE courses SET course_name = ? WHERE module_id = ? AND course_name = ?",
                    (new_name, module_id[0], old_name)
                )
                conn.commit()
                return "success"
            return "module_not_found"
    except sqlite3.IntegrityError:
        return "duplicate_course"

def delete_cours(module_name: str, course_name: str, user_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM modules WHERE module_name = ? AND user_id = ?", (module_name, user_id))
        module_id = cursor.fetchone()
        if module_id:
            cursor.execute("SELECT id FROM courses WHERE module_id = ? AND course_name = ?", (module_id[0], course_name))
            course_id = cursor.fetchone()
            if course_id:
                cursor.execute("DELETE FROM flashcards WHERE course_id = ?", (course_id[0],))
                cursor.execute("DELETE FROM courses WHERE id = ?", (course_id[0],))
                conn.commit()

def add_flashcard(module_name: str, course_name: str, front: str, back: str, user_id: int, photo_path: str = None) -> str:
    try:
        with sqlite3.connect("bot_data.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM courses
                WHERE course_name = ?
                AND module_id = (
                    SELECT id FROM modules
                    WHERE module_name = ? AND user_id = ?
                )
            """, (course_name, module_name, user_id))
            course_id = cursor.fetchone()
            if course_id:
                cursor.execute("""
                    INSERT INTO flashcards (course_id, front, back, next_review, interval, photo_path)
                    VALUES (?, ?, ?, datetime('now'), 1, ?)
                """, (course_id[0], front, back, photo_path))
                conn.commit()
                return "success"
            return "invalid_course"
    except sqlite3.IntegrityError:
        return "duplicate_flashcard"

def get_flashcards(module_name: str, course_name: str, user_id: int) -> list:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, front, back, created_at, next_review, interval, photo_path FROM flashcards
            WHERE course_id = (SELECT id FROM courses WHERE course_name = ?
                              AND module_id = (SELECT id FROM modules WHERE module_name = ? AND user_id = ?))
        """, (course_name, module_name, user_id))
        flashcards = [{
            "id": row[0],
            "front": row[1],
            "back": row[2],
            "created_at": row[3],
            "next_review": row[4],
            "interval": row[5],
            "photo_path": row[6]
        } for row in cursor.fetchall()]
    return flashcards

def delete_flashcard_by_id(flashcard_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
        conn.commit()

def modify_flashcard(flashcard_id: int, new_front: str = None, new_back: str = None, new_photo_path: str = None) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        if new_front and new_back:
            cursor.execute(
                "UPDATE flashcards SET front = ?, back = ?, photo_path = ? WHERE id = ?",
                (new_front, new_back, new_photo_path, flashcard_id)
            )
        elif new_front:
            cursor.execute(
                "UPDATE flashcards SET front = ?, photo_path = ? WHERE id = ?",
                (new_front, new_photo_path, flashcard_id)
            )
        elif new_back:
            cursor.execute(
                "UPDATE flashcards SET back = ?, photo_path = ? WHERE id = ?",
                (new_back, new_photo_path, flashcard_id)
            )
        conn.commit()

def get_due_flashcards(module_name: str, course_name: str, user_id: int) -> list:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, front, back, created_at, next_review, interval FROM flashcards
            WHERE course_id = (SELECT id FROM courses WHERE course_name = ?
                              AND module_id = (SELECT id FROM modules WHERE module_name = ? AND user_id = ?))
            AND next_review <= datetime('now')
        """, (course_name, module_name, user_id))
        flashcards = [{
            "id": row[0],
            "front": row[1],
            "back": row[2],
            "created_at": row[3],
            "next_review": row[4],
            "interval": row[5]
        } for row in cursor.fetchall()]
    return flashcards

def update_flashcard_review(module_name: str, course_name: str, flashcard_id: int, remembered: bool, user_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, interval FROM flashcards
            WHERE course_id = (SELECT id FROM courses WHERE course_name = ?
                              AND module_id = (SELECT id FROM modules WHERE module_name = ? AND user_id = ?))
            AND id = ?
        """, (course_name, module_name, user_id, flashcard_id))
        flashcard = cursor.fetchone()
        if flashcard:
            current_interval = flashcard[1]
            if remembered:
                new_interval = current_interval * 2
                next_review = datetime.now() + timedelta(days=new_interval)
            else:
                new_interval = 1
                next_review = datetime.now() + timedelta(days=new_interval)
            cursor.execute("""
                UPDATE flashcards
                SET interval = ?, next_review = ?
                WHERE id = ?
            """, (new_interval, next_review, flashcard[0]))
            conn.commit()

def add_schedule(conn, user_id, module_name, course_name, flashcard_id, revision_day, revision_time):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO schedules (user_id, module_name, course_name, flashcard_id, revision_day, revision_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, module_name, course_name, flashcard_id, revision_day, revision_time))
    conn.commit()

def get_schedules(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def delete_schedule(conn, schedule_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()
