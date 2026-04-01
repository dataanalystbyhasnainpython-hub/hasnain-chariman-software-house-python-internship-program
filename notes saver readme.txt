NOTES SAVER APPLICATION - README
================================

FILE HANDLING LOGIC
-------------------

The application uses a simple text file "notes.txt" for data storage with the following approach:

1. FILE CREATION:
   When the program starts, it attempts to open "notes.txt" in read mode.
   If the file doesn't exist, it creates an empty file automatically.
   This ensures the program never crashes due to missing file.

2. WRITING NOTES (Add Note Feature):
   Uses append mode to add new notes.
   Each note includes a timestamp in format [YYYY-MM-DD HH:MM:SS].
   New notes are added to the end of file without overwriting existing content.
   Format example: [2024-01-15 14:30:25] This is my note content

3. READING NOTES (View Notes Feature):
   Uses read mode to open and read all notes.
   Reads all lines from file using readlines operation.
   Filters out empty lines for clean display.
   Displays notes with sequential numbers for easy reference.

4. DELETING NOTES (Delete Note Feature):
   Reads all existing notes from file.
   Stores them in a list structure.
   Removes the selected note from the list.
   Uses write mode to completely rewrite the file.
   Writes back all remaining notes which overwrites the file completely.

5. SEARCHING NOTES (Search Notes Feature):
   Reads all notes from file.
   Performs case insensitive search.
   Displays only matching notes with their original positions.

KEY FILE HANDLING CONCEPTS USED:
--------------------------------

MODES:
   Read Mode - Used for viewing, searching, and reading existing notes
   Write Mode - Used for rewriting file after deletions
   Append Mode - Used for adding new notes without overwriting

OPERATIONS:
   Open - Opens the file with specified mode
   Readlines - Reads all lines into a list
   Write - Writes content to file
   Close - Closes the file to free resources

ERROR HANDLING:
   Try except blocks catch file related errors
   Prevents program crash if file operations fail
   Provides user friendly error messages

FEATURES IMPLEMENTED:
--------------------

Required Features:
   Add New Note - Takes input and saves to file with timestamp
   View Saved Notes - Reads and displays all notes in numbered format
   Exit Option - Clean exit with confirmation message

Bonus Features:
   Date Time Stamp - Each note automatically gets timestamp
   Delete Specific Notes - Users can delete notes by their number
   Search Notes by Keyword - Find notes containing specific text
   Functions for Each Feature - Modular design with separate functions
   Format Notes Cleanly - Numbered list with timestamps for easy reading

HOW TO USE:
-----------

1. Run the program
2. Choose option 1 to add a new note
3. Choose option 2 to view all saved notes
4. Choose option 3 to delete a specific note
5. Choose option 4 to search notes by keyword
6. Choose option 5 to exit the program

The program automatically creates and manages the notes.txt file in the same directory.
All notes are preserved between program sessions.