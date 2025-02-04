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

# def modify_cours(old_name: str, new_name: str, user_id: int, module_id: int) -> str:
#     try:
#         with sqlite3.connect("bot_data.db") as conn:
#             cursor = conn.cursor()

#             # Update the course name in the modules table
#             cursor.execute(
#                 "UPDATE modules SET module_name = ? WHERE module_name = ? AND user_id = ? AND id = ?",
#                 (new_name, old_name, user_id, module_id)
#             )

#             conn.commit()
#             return "success"
#     except sqlite3.IntegrityError:
#         return "duplicate_cours"

def modify_cours(module_name: str, old_name: str, new_name: str, user_id: int) -> str:
    try:
        with sqlite3.connect("bot_data.db") as conn:
            cursor = conn.cursor()
            
            # Get the module_id
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
        
# def delete_cours(course_name: str, user_id: int, module_id: int) -> None:
#     with sqlite3.connect("bot_data.db") as conn:
#         cursor = conn.cursor()

#         # Get the course ID associated with the module
#         cursor.execute("""
#             SELECT id FROM courses
#             WHERE course_name = ? AND module_id = ? AND EXISTS (
#                 SELECT 1 FROM modules WHERE id = ? AND user_id = ?
#             )
#         """, (course_name, module_id, module_id, user_id))

#         course_id = cursor.fetchone()

#         if course_id:
#             # Delete flashcards related to this course
#             cursor.execute("""
#                 DELETE FROM flashcards WHERE course_id = ?
#             """, (course_id[0],))

#             # Delete the specific course
#             cursor.execute("""
#                 DELETE FROM courses WHERE id = ?
#             """, (course_id[0],))

#             conn.commit()
#         else:
#             print("Course not found or does not belong to the module.")

def delete_cours(module_name: str, course_name: str, user_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        
        # Get the module_id
        cursor.execute("SELECT id FROM modules WHERE module_name = ? AND user_id = ?", (module_name, user_id))
        module_id = cursor.fetchone()
        
        if module_id:
            # Get the course_id
            cursor.execute("SELECT id FROM courses WHERE module_id = ? AND course_name = ?", (module_id[0], course_name))
            course_id = cursor.fetchone()
            
            if course_id:
                # Delete flashcards
                cursor.execute("DELETE FROM flashcards WHERE course_id = ?", (course_id[0],))
                # Delete course
                cursor.execute("DELETE FROM courses WHERE id = ?", (course_id[0],))
                conn.commit()

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


def delete_flashcard_by_id(flashcard_id: int) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
        conn.commit()

def modify_flashcard(flashcard_id: int, new_front: str = None, new_back: str = None) -> None:
    with sqlite3.connect("bot_data.db") as conn:
        cursor = conn.cursor()
        if new_front and new_back:
            cursor.execute(
                "UPDATE flashcards SET front = ?, back = ? WHERE id = ?",
                (new_front, new_back, flashcard_id)
            )
        elif new_front:
            cursor.execute(
                "UPDATE flashcards SET front = ? WHERE id = ?",
                (new_front, flashcard_id)
            )
        elif new_back:
            cursor.execute(
                "UPDATE flashcards SET back = ? WHERE id = ?",
                (new_back, flashcard_id)
            )
        conn.commit()