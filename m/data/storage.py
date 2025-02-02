import sqlite3
from datetime import datetime, timedelta

# Function to create the database and tables
def create_db():
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()

        # Create table for modules
        cursor.execute('''
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        module_name TEXT NOT NULL,
        UNIQUE(user_id, module_name)  -- Ensures unique module names per user
    )
''')


        # Create table for courses
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            course_name TEXT NOT NULL,
            FOREIGN KEY (module_id) REFERENCES modules(id)
        )
        ''')

        # Create table for flashcards
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            next_review DATETIME,
            interval INTEGER DEFAULT 1,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
        ''')

        # Add indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_modules_user_id ON modules (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_courses_module_id ON courses (module_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_flashcards_course_id ON flashcards (course_id)")

        conn.commit()

create_db()
print("Database and tables created successfully.")

# Add Module
def add_module(module_name: str, user_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO modules (user_id, module_name) VALUES (?, ?)", (user_id, module_name))
        conn.commit()

# Get Modules for a specific user
def get_modules(user_id: int) -> list:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT module_name FROM modules WHERE user_id = ?", (user_id,))
        modules = [row[0] for row in cursor.fetchall()]
    return modules


# Add Course to a module
def add_course(module_name: str, course_name: str, user_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()

        # Get the module_id for the specified module
        cursor.execute("SELECT id FROM modules WHERE module_name = ? AND user_id = ?", (module_name, user_id))
        module_id = cursor.fetchone()

        if module_id:
            cursor.execute("INSERT INTO courses (module_id, course_name) VALUES (?, ?)", (module_id[0], course_name))
            conn.commit()

# Get Courses for a Module
def get_courses(module_name: str, user_id: int) -> list:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT course_name FROM courses
            WHERE module_id = (SELECT id FROM modules WHERE module_name = ? AND user_id = ?)
        """, (module_name, user_id))
        courses = [row[0] for row in cursor.fetchall()]
    return courses

# Add Flashcard to a course
def add_flashcard(module_name: str, course_name: str, front: str, back: str, user_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()

        # Get course_id
        cursor.execute("""
            SELECT id FROM courses 
            WHERE course_name = ? AND module_id = (SELECT id FROM modules WHERE module_name = ? AND user_id = ?)
        """, (course_name, module_name, user_id))
        course_id = cursor.fetchone()

        if course_id:
            cursor.execute("""
                INSERT INTO flashcards (course_id, front, back, next_review, interval) 
                VALUES (?, ?, ?, datetime('now'), 1)
            """, (course_id[0], front, back))
            conn.commit()

# Get Flashcards for a specific Course
def get_flashcards(module_name: str, course_name: str, user_id: int) -> list:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, front, back, created_at, next_review, interval FROM flashcards
            WHERE course_id = (SELECT id FROM courses WHERE course_name = ? 
                              AND module_id = (SELECT id FROM modules WHERE module_name = ? AND user_id = ?))
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

# Get Due Flashcards
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

# Update Flashcard Review
def update_flashcard_review(module_name: str, course_name: str, flashcard_id: int, remembered: bool, user_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()

        # Get the flashcard
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
                # Double the interval
                new_interval = current_interval * 2
                next_review = datetime.now() + timedelta(days=new_interval)
            else:
                # Reset the interval to 1 day
                new_interval = 1
                next_review = datetime.now() + timedelta(days=new_interval)

            # Update the flashcard
            cursor.execute("""
                UPDATE flashcards 
                SET interval = ?, next_review = ?
                WHERE id = ?
            """, (new_interval, next_review, flashcard[0]))
            conn.commit()