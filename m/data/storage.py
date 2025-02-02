import sqlite3
from datetime import datetime, timedelta

# Function to create the database and tables
def create_db():
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()

        # Create tables with unique constraints
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
            UNIQUE(course_id, front),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
        ''')

        conn.commit()

create_db()
print("Database and tables created successfully.")

# Add Module
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
    
# Get Modules for a specific user
def get_modules(user_id: int) -> list:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT module_name FROM modules WHERE user_id = ?", (user_id,))
        modules = [row[0] for row in cursor.fetchall()]
    return modules

# Function to get the module_id based on the module_name
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
                return result[0]  # Return the module_id
            else:
                return None  # Return None if module_name doesn't exist
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

        # Get the module ID
        cursor.execute("SELECT id FROM modules WHERE module_name = ? AND user_id = ?", (module_name, user_id))
        module_id = cursor.fetchone()

        if module_id:
            # Delete all flashcards associated with the module's courses
            cursor.execute("""
                DELETE FROM flashcards 
                WHERE course_id IN (
                    SELECT id FROM courses WHERE module_id = ?
                )
            """, (module_id[0],))

            # Delete all courses associated with the module
            cursor.execute("DELETE FROM courses WHERE module_id = ?", (module_id[0],))

            # Delete the module
            cursor.execute("DELETE FROM modules WHERE id = ?", (module_id[0],))

            conn.commit()


# Add Course to a module
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
def add_flashcard(module_name: str, course_name: str, front: str, back: str, user_id: int) -> str:
    try:
        with sqlite3.connect("bot_data.db") as conn:
            cursor = conn.cursor()

            # Get course_id
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
                    INSERT INTO flashcards (course_id, front, back, next_review, interval) 
                    VALUES (?, ?, ?, datetime('now'), 1)
                """, (course_id[0], front, back))
                conn.commit()
                return "success"
            return "invalid_course"
    except sqlite3.IntegrityError:
        return "duplicate_flashcard"
    
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