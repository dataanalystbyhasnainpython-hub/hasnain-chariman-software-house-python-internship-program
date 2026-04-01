def ensurefileexists():
    """Create the notes file if it doesn't exist"""
    try:
        testfile = open("notes.txt", 'r')
        testfile.close()
    except:
        try:
            file = open("notes.txt", 'w')
            file.close()
        except Exception as e:
            print(f"Error creating file: {e}")
def gettimestamp():
    """Get current timestamp as string"""
    import time
    currenttime = time.localtime()
    timestamp = f"{currenttime.tm_year}-{currenttime.tm_mon:02d}-{currenttime.tm_mday:02d} {currenttime.tm_hour:02d}:{currenttime.tm_min:02d}:{currenttime.tm_sec:02d}"
    return timestamp
def addnote():
    """Add a new note with timestamp"""
    print("\n--- Add New Note ---")
    notetext = input("Enter your note: ")
    if not notetext.strip():
        print("Note cannot be empty!")
        return
    timestamp = gettimestamp()
    try:
        file = open("notes.txt", 'a')
        file.write(f"[{timestamp}] {notetext}\n")
        file.close()
        print("Note saved successfully!")
    except Exception as e:
        print(f"Error saving note: {e}")
def viewnotes():
    """Display all saved notes in a formatted way"""
    print("\n--- Saved Notes ---")
    try:
        file = open("notes.txt", 'r')
        notes = file.readlines()
        file.close()
        cleannotes = []
        for note in notes:
            if note.strip():
                cleannotes.append(note.strip())
        if not cleannotes:
            print("No notes found. Please add some notes first.")
            return
        for i in range(len(cleannotes)):
            print(f"{i + 1}. {cleannotes[i]}")
    except:
        print("No notes found. Please add a note first.")
def deletenote():
    """Delete a specific note by its number"""
    print("\n--- Delete Note ---")
    try:
        file = open("notes.txt", 'r')
        notes = file.readlines()
        file.close()
        cleannotes = []
        for note in notes:
            if note.strip():
                cleannotes.append(note.strip())
        if not cleannotes:
            print("No notes to delete.")
            return
        print("Select a note to delete:")
        for i in range(len(cleannotes)):
            print(f"{i + 1}. {cleannotes[i]}")
        try:
            choice = input("\nEnter note number to delete (0 to cancel): ")
            choice = int(choice)
            if choice == 0:
                print("Deletion cancelled.")
                return
            if 1 <= choice <= len(cleannotes):
                deletednote = cleannotes.pop(choice - 1)
                file = open("notes.txt", 'w')
                for note in cleannotes:
                    file.write(f"{note}\n")
                file.close()
                print(f"Note deleted successfully: {deletednote}")
            else:
                print("Invalid note number.")
        except ValueError:
            print("Please enter a valid number.")
    except:
        print("No notes file found.")
def searchnotes():
    """Search for notes containing a specific keyword"""
    print("\n--- Search Notes ---")
    keyword = input("Enter search keyword: ")
    if not keyword.strip():
        print("Search keyword cannot be empty!")
        return
    try:
        file = open("notes.txt", 'r')
        notes = file.readlines()
        file.close()
        cleannotes = []
        for note in notes:
            if note.strip():
                cleannotes.append(note.strip())
        if not cleannotes:
            print("No notes found.")
            return
        matchingnotes = []
        for i in range(len(cleannotes)):
            if keyword.lower() in cleannotes[i].lower():
                matchingnotes.append((i + 1, cleannotes[i]))
        if matchingnotes:
            print(f"\nFound {len(matchingnotes)} matching note(s):")
            for notenum, note in matchingnotes:
                print(f"{notenum}. {note}")
        else:
            print(f"No notes found containing '{keyword}'.")
    except:
        print("No notes file found.")
def displaymenu():
    """Display the main menu options"""
    print("\n" + "=" * 30)
    print("     NOTES SAVER APPLICATION")
    print("=" * 30)
    print("1. Add Note")
    print("2. View Notes")
    print("3. Delete Note")
    print("4. Search Notes")
    print("5. Exit")
    print("-" * 30)
def main():
    """Main application loop"""
    ensurefileexists()
    print("\n"+"="* 30)
    print("Welcome to Notes Saver Application!")
    print("\n" + "=" * 30)
    while True:
        displaymenu()
        choice = input("Choose an option (1-5): ")
        if choice == "1":
            addnote()
        elif choice == "2":
            viewnotes()
        elif choice == "3":
            deletenote()
        elif choice == "4":
            searchnotes()
        elif choice == "5":
            print("\nThank you for using Notes Saver!")
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1-5.")
        input("\nPress Enter to continue...")
# Program entry point
if __name__ == "__main__":
    main()