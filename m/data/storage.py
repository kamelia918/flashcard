from datetime import datetime, timedelta

# In-memory storage for modules, courses, and flashcards
_modules = {}

def add_module(module_name: str) -> None:
    if module_name not in _modules:
        _modules[module_name] = {}  # Initialize an empty dictionary for courses

def get_modules() -> list:
    return list(_modules.keys())

def add_course(module_name: str, course_name: str) -> None:
    if module_name in _modules:
        _modules[module_name][course_name] = []  # Initialize an empty list of flashcards for the course

def get_courses(module_name: str) -> list:
    return list(_modules.get(module_name, {}).keys())

def add_flashcard(module_name: str, course_name: str, front: str, back: str) -> None:
    if module_name in _modules and course_name in _modules[module_name]:
        flashcard = {
            "front": front,
            "back": back,
            "created_at": datetime.now(),  # Store creation date
            "next_review": datetime.now(),  # First review is immediately
            "interval": timedelta(days=1)  # Initial interval
        }
        _modules[module_name][course_name].append(flashcard)

def get_flashcards(module_name: str, course_name: str) -> list:
    return _modules.get(module_name, {}).get(course_name, [])

def get_due_flashcards(module_name: str, course_name: str) -> list:
    now = datetime.now()
    flashcards = get_flashcards(module_name, course_name)
    return [flashcard for flashcard in flashcards if flashcard["next_review"] <= now]

def update_flashcard_review(module_name: str, course_name: str, flashcard_index: int, remembered: bool) -> None:
    if module_name in _modules and course_name in _modules[module_name]:
        flashcard = _modules[module_name][course_name][flashcard_index]
        if remembered:
            # Increase the interval (e.g., double it)
            flashcard["interval"] *= 2
        else:
            # Reset the interval to 1 day
            flashcard["interval"] = timedelta(days=1)
        # Update the next review date
        flashcard["next_review"] = datetime.now() + flashcard["interval"]



