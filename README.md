# The bot we are modifying is:  
@AspirantFC_bot  

code is inside the memorist-bot folder

# The hosted bot is:  
@memorist  

# command to run the code : 

python main.py

# TO-DO
* Integrate a database to store created flashcards.
* Add functionality to modify or delete existing flashcards.
* Implement revision methods, such as spaced repetition + sends automated reminders to review a certain card or a certain deck of cards (generallt a deck of cards) 
* Develop an AI model to suggest specific modules or courses that need review.
* Ensure that users only see their own flashcards, rather than all users' cards.
* adding the ability to add your kwn revision timers for certain decks
* adding a ddl

#  Database Schema

* modules	id (INTEGER PRIMARY KEY), user_id (INTEGER), module_name (TEXT)	 --> Stores modules per user
* courses	id (INTEGER PRIMARY KEY), module_id (INTEGER FOREIGN KEY), course_name (TEXT) -->	Each course belongs to a module
* flashcards	id (INTEGER PRIMARY KEY), course_id (INTEGER FOREIGN KEY), question (TEXT), answer (TEXT)	)--> Each flashcard belongs to a course
