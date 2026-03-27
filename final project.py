#final project  task 6 all in one
# =============================================================================
# ANSI Color Codes for Colorful CLI Output
# =============================================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
# =============================================================================
# Utility Functions
# =============================================================================
def clearScreen():
    """Clear the terminal screen using simple newlines."""
    print("\n" * 30)
def printHeader(title):
    """Print a formatted header for menu sections with colors."""
    print(Colors.CYAN + Colors.BOLD + "=" * 60 + Colors.END)
    print(Colors.YELLOW + Colors.BOLD + "  " + title + Colors.END)
    print(Colors.CYAN + Colors.BOLD + "=" * 60 + Colors.END)
def printError(message):
    """Print error messages in red color."""
    print(Colors.RED + Colors.BOLD + "[ERROR] " + message + Colors.END)
def printSuccess(message):
    """Print success messages in green color."""
    print(Colors.GREEN + Colors.BOLD + "[SUCCESS] " + message + Colors.END)
def printInfo(message):
    """Print info messages in blue color."""
    print(Colors.BLUE + message + Colors.END)
def printWarning(message):
    """Print warning messages in yellow color."""
    print(Colors.YELLOW + message + Colors.END)
def waitForEnter():
    """Pause execution until user presses Enter."""
    input(Colors.CYAN + "Press Enter to continue..." + Colors.END)
def getValidNumber(prompt):
    """Get a valid number from user input with error handling."""
    while True:
        try:
            value = float(input(Colors.WHITE + prompt + Colors.END))
            return value
        except ValueError:
            printError("Invalid input. Please enter a valid number.")
def getValidInteger(prompt, allowNegative=False):
    """Get a valid integer from user input."""
    while True:
        try:
            value = int(input(Colors.WHITE + prompt + Colors.END))
            if not allowNegative and value < 0:
                printError("Please enter a non-negative integer.")
                continue
            return value
        except ValueError:
            printError("Invalid input. Please enter a valid integer.")
# =============================================================================
# Feature 1: Calculator
# =============================================================================
def calculatorMenu():
    """Display calculator sub-menu and perform operations."""
    while True:
        clearScreen()
        printHeader("CALCULATOR")
        print(Colors.GREEN + "1. Addition" + Colors.END)
        print(Colors.GREEN + "2. Subtraction" + Colors.END)
        print(Colors.GREEN + "3. Multiplication" + Colors.END)
        print(Colors.GREEN + "4. Division" + Colors.END)
        print(Colors.RED + "5. Back to Main Menu" + Colors.END)
        choice = input(Colors.WHITE + "Select an operation (1-5): " + Colors.END).strip()
        if choice == "5":
            break
        if choice in ["1", "2", "3", "4"]:
            num1 = getValidNumber("Enter first number: ")
            num2 = getValidNumber("Enter second number: ")
            if choice == "1":
                result = num1 + num2
                print(Colors.GREEN + Colors.BOLD + "Result: " + str(num1) + " + " + str(num2) + " = " + str(
                    result) + Colors.END)
            elif choice == "2":
                result = num1 - num2
                print(Colors.GREEN + Colors.BOLD + "Result: " + str(num1) + " - " + str(num2) + " = " + str(
                    result) + Colors.END)
            elif choice == "3":
                result = num1 * num2
                print(Colors.GREEN + Colors.BOLD + "Result: " + str(num1) + " * " + str(num2) + " = " + str(
                    result) + Colors.END)
            elif choice == "4":
                if num2 == 0:
                    printError("Division by zero is not allowed.")
                else:
                    result = num1 / num2
                    print(Colors.GREEN + Colors.BOLD + "Result: " + str(num1) + " / " + str(num2) + " = " + str(
                        result) + Colors.END)
        else:
            printError("Invalid choice. Please select 1-5.")
        waitForEnter()
# =============================================================================
# Feature 2: Pattern Generator
# =============================================================================
def patternMenu():
    """Display pattern generator sub-menu."""
    while True:
        clearScreen()
        printHeader("PATTERN GENERATOR")
        print(Colors.GREEN + "1. Star Pattern (Triangle)" + Colors.END)
        print(Colors.GREEN + "2. Number Pattern (Pyramid)" + Colors.END)
        print(Colors.RED + "3. Back to Main Menu" + Colors.END)
        choice = input(Colors.WHITE + "Select an option (1-3): " + Colors.END).strip()
        if choice == "3":
            break
        if choice in ["1", "2"]:
            rows = getValidInteger("Enter number of rows: ", allowNegative=False)
            if choice == "1":
                print(Colors.YELLOW + "Star Pattern:" + Colors.END)
                for i in range(1, rows + 1):
                    print(Colors.CYAN + "*" * i + Colors.END)
            elif choice == "2":
                print(Colors.YELLOW + "Number Pattern:" + Colors.END)
                for i in range(1, rows + 1):
                    line = ""
                    for j in range(1, i + 1):
                        line = line + str(j) + " "
                    print(Colors.CYAN + line + Colors.END)
        else:
            printError("Invalid choice. Please select 1-3.")
        waitForEnter()
# =============================================================================
# Feature 3: File Handling System
# =============================================================================
DATAFILE = "appdata.txt"
def loadData():
    """Load data from text file."""
    try:
        with open(DATAFILE, "r") as file:
            content = file.read()
            if content.strip():
                return content.strip().split("\n")
            return []
    except:
        return []
def saveData(data):
    """Save data to text file."""
    try:
        with open(DATAFILE, "w") as file:
            file.write("\n".join(data))
        return True
    except:
        return False
def fileHandlingMenu():
    """Display file handling sub-menu."""
    while True:
        clearScreen()
        printHeader("FILE HANDLING SYSTEM")
        print(Colors.GREEN + "1. Add Data to File" + Colors.END)
        print(Colors.GREEN + "2. View All Stored Data" + Colors.END)
        print(Colors.RED + "3. Delete All Data" + Colors.END)
        print(Colors.RED + "4. Back to Main Menu" + Colors.END)
        choice = input(Colors.WHITE + "Select an option (1-4): " + Colors.END).strip()
        if choice == "4":
            break
        if choice == "1":
            data = loadData()
            entry = input(Colors.WHITE + "Enter data to store: " + Colors.END).strip()
            if entry:
                data.append(entry)
                if saveData(data):
                    printSuccess("Data added successfully!")
                else:
                    printError("Failed to save data.")
            else:
                printError("Data cannot be empty.")
        elif choice == "2":
            data = loadData()
            if not data:
                printWarning("No data found. The file is empty.")
            else:
                print(Colors.YELLOW + "Stored Data:" + Colors.END)
                print(Colors.CYAN + "-" * 40 + Colors.END)
                for idx, item in enumerate(data, 1):
                    print(Colors.WHITE + str(idx) + ". " + item + Colors.END)
                print(Colors.CYAN + "-" * 40 + Colors.END)
        elif choice == "3":
            confirm = input(
                Colors.RED + "Are you sure you want to delete all data? (yes/no): " + Colors.END).strip().lower()
            if confirm == "yes":
                if saveData([]):
                    printSuccess("All data has been deleted.")
                else:
                    printError("Failed to delete data.")
            else:
                printInfo("Deletion cancelled.")
        else:
            printError("Invalid choice. Please select 1-4.")
        waitForEnter()
# =============================================================================
# Feature 4: Number Utilities
# =============================================================================
def isEven(number):
    """Check if a number is even."""
    return number % 2 == 0
def isPrime(number):
    """Check if a number is prime."""
    if number <= 1:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True
def multiplicationTable(number):
    """Generate multiplication table for a number."""
    print(Colors.YELLOW + "Multiplication Table for " + str(number) + ":" + Colors.END)
    print(Colors.CYAN + "-" * 30 + Colors.END)
    for i in range(1, 11):
        print(Colors.GREEN + str(number) + " x " + str(i) + " = " + str(number * i) + Colors.END)
def numberUtilitiesMenu():
    """Display number utilities sub-menu."""
    while True:
        clearScreen()
        printHeader("NUMBER UTILITIES")
        print(Colors.GREEN + "1. Check Even or Odd" + Colors.END)
        print(Colors.GREEN + "2. Check Prime Number" + Colors.END)
        print(Colors.GREEN + "3. Generate Multiplication Table" + Colors.END)
        print(Colors.RED + "4. Back to Main Menu" + Colors.END)
        choice = input(Colors.WHITE + "Select an option (1-4): " + Colors.END).strip()
        if choice == "4":
            break
        if choice in ["1", "2"]:
            num = getValidInteger("Enter a number: ")
            if choice == "1":
                if isEven(num):
                    print(Colors.GREEN + str(num) + " is an EVEN number." + Colors.END)
                else:
                    print(Colors.YELLOW + str(num) + " is an ODD number." + Colors.END)
            elif choice == "2":
                if isPrime(num):
                    print(Colors.GREEN + str(num) + " is a PRIME number." + Colors.END)
                else:
                    print(Colors.RED + str(num) + " is NOT a prime number." + Colors.END)
        elif choice == "3":
            num = getValidInteger("Enter a number: ", allowNegative=False)
            multiplicationTable(num)
        else:
            printError("Invalid choice. Please select 1-4.")
        waitForEnter()
# =============================================================================
# Feature 5: Simple Quiz System
# =============================================================================
def runQuiz():
    """Run the quiz and display results."""
    questions = [
        {
            "question": "What is the capital of France?",
            "options": ["A. London", "B. Berlin", "C. Paris", "D. Madrid"],
            "answer": "C"
        },
        {
            "question": "Which programming language is this application written in?",
            "options": ["A. Java", "B. Python", "C. C++", "D. JavaScript"],
            "answer": "B"
        },
        {
            "question": "What is 15 + 7?",
            "options": ["A. 20", "B. 21", "C. 22", "D. 23"],
            "answer": "C"
        },
        {
            "question": "Which of the following is used for file handling in Python?",
            "options": ["A. open()", "B. read()", "C. write()", "D. All of the above"],
            "answer": "D"
        },
        {
            "question": "What does CLI stand for?",
            "options": ["A. Command Line Interface", "B. Common Language Input", "C. Computer Language Instruction",
                        "D. Code Line Integration"],
            "answer": "A"
        }
    ]
    score = 0
    printHeader("QUIZ TIME")
    print(Colors.WHITE + "Answer the following questions. Enter A, B, C, or D." + Colors.END)
    for idx, q in enumerate(questions, 1):
        print(Colors.YELLOW + Colors.BOLD + "Question " + str(idx) + ": " + q["question"] + Colors.END)
        for opt in q["options"]:
            print(Colors.CYAN + "  " + opt + Colors.END)
        while True:
            answer = input(Colors.GREEN + "Your answer: " + Colors.END).strip().upper()
            if answer in ["A", "B", "C", "D"]:
                break
            printError("Invalid input. Please enter A, B, C, or D.")
        if answer == q["answer"]:
            print(Colors.GREEN + "Correct!" + Colors.END)
            score += 1
        else:
            print(Colors.RED + "Wrong! The correct answer was " + q["answer"] + "." + Colors.END)
        print()
    printHeader("QUIZ COMPLETED")
    print(Colors.GREEN + Colors.BOLD + "Your Score: " + str(score) + " out of " + str(len(questions)) + Colors.END)
    percentage = (score / len(questions)) * 100
    if percentage >= 70:
        print(Colors.GREEN + "Percentage: " + str(percentage) + "%" + Colors.END)
    elif percentage >= 40:
        print(Colors.YELLOW + "Percentage: " + str(percentage) + "%" + Colors.END)
    else:
        print(Colors.RED + "Percentage: " + str(percentage) + "%" + Colors.END)
    scoreFile = "quizscores.txt"
    try:
        with open(scoreFile, "a") as file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(
                timestamp + " - Score: " + str(score) + "/" + str(len(questions)) + " - " + str(percentage) + "%\n")
        printSuccess("Your score has been saved!")
    except:
        printError("Failed to save score.")
    waitForEnter()
def viewQuizHistory():
    """Display all saved quiz scores."""
    scoreFile = "quizscores.txt"
    clearScreen()
    printHeader("QUIZ SCORE HISTORY")
    try:
        with open(scoreFile, "r") as file:
            content = file.read()
            if content.strip():
                print(Colors.CYAN + content + Colors.END)
            else:
                printWarning("No quiz scores found. Take the quiz first!")
    except:
        printWarning("No quiz scores found. Take the quiz first!")
    waitForEnter()
def quizMenu():
    """Display quiz sub-menu."""
    while True:
        clearScreen()
        printHeader("QUIZ SYSTEM")
        print(Colors.GREEN + "1. Take a Quiz" + Colors.END)
        print(Colors.GREEN + "2. View Score History" + Colors.END)
        print(Colors.RED + "3. Back to Main Menu" + Colors.END)
        choice = input(Colors.WHITE + "Select an option (1-3): " + Colors.END).strip()
        if choice == "3":
            break
        elif choice == "1":
            runQuiz()
        elif choice == "2":
            viewQuizHistory()
        else:
            printError("Invalid choice. Please select 1-3.")
            waitForEnter()
# =============================================================================
# Bonus Feature: Login System
# =============================================================================
def loginSystem():
    """Simple username/password login system."""
    attempts = 3
    while attempts > 0:
        clearScreen()
        printHeader("LOGIN SYSTEM")
        print(Colors.YELLOW + "Default credentials: admin / password123" + Colors.END)
        print(Colors.RED + "Attempts remaining: " + str(attempts) + Colors.END)
        username = input(Colors.GREEN + "Username: " + Colors.END).strip()
        password = input(Colors.GREEN + "Password: " + Colors.END).strip()
        if username == "admin" and password == "password123":
            printSuccess("Login successful!")
            waitForEnter()
            return True
        else:
            attempts -= 1
            printError("Invalid credentials. " + str(attempts) + " attempts remaining.")
            if attempts > 0:
                waitForEnter()
    printError("Too many failed attempts. Exiting application.")
    return False
# =============================================================================
# Bonus Feature: Password Generator (Without random import)
# =============================================================================
def generatePassword():
    """Generate a simple password using basic logic."""
    length = getValidInteger("Enter desired password length (min 6): ", allowNegative=False)
    if length < 6:
        printError("Password length should be at least 6 characters.")
        length = 6
    vowels = "aeiou"
    consonants = "bcdfghjklmnpqrstvwxyz"
    numbers = "0123456789"
    symbols = "!@#$"
    password = ""
    for i in range(length):
        if i % 4 == 0:
            import time
            seed = int(time.time() * 1000) % 26
            password = password + consonants[seed % len(consonants)]
        elif i % 4 == 1:
            import time
            seed = int(time.time() * 1000) % 26
            password = password + vowels[seed % len(vowels)]
        elif i % 4 == 2:
            import time
            seed = int(time.time() * 1000) % 10
            password = password + numbers[seed % len(numbers)]
        else:
            import time
            seed = int(time.time() * 1000) % 4
            password = password + symbols[seed % len(symbols)]
    print(Colors.YELLOW + "Generated Password: " + Colors.END + Colors.GREEN + Colors.BOLD + password + Colors.END)
    printSuccess("Password generated! (Remember to store it safely)")
    waitForEnter()
def notesMenu():
    """Simple notes application."""
    NOTES_FILE = "mynotes.txt"
    while True:
        clearScreen()
        printHeader("NOTES APP")
        print(Colors.GREEN + "1. Write a New Note" + Colors.END)
        print(Colors.GREEN + "2. Read All Notes" + Colors.END)
        print(Colors.RED + "3. Clear All Notes" + Colors.END)
        print(Colors.RED + "4. Back to Main Menu" + Colors.END)
        choice = input(Colors.WHITE + "Select an option (1-4): " + Colors.END).strip()
        if choice == "4":
            break
        if choice == "1":
            note = input(Colors.WHITE + "Enter your note: " + Colors.END).strip()
            if note:
                try:
                    with open(NOTES_FILE, "a") as file:
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        file.write("[" + timestamp + "] " + note + "\n")
                    printSuccess("Note saved!")
                except:
                    printError("Failed to save note.")
            else:
                printError("Note cannot be empty.")

        elif choice == "2":
            try:
                with open(NOTES_FILE, "r") as file:
                    content = file.read()
                    if content:
                        print(Colors.YELLOW + "Your Notes:" + Colors.END)
                        print(Colors.CYAN + "-" * 50 + Colors.END)
                        print(Colors.WHITE + content + Colors.END)
                    else:
                        printWarning("No notes found.")
            except:
                printWarning("No notes found. Create your first note!")
        elif choice == "3":
            confirm = input(
                Colors.RED + "Are you sure you want to clear all notes? (yes/no): " + Colors.END).strip().lower()
            if confirm == "yes":
                try:
                    with open(NOTES_FILE, "w") as file:
                        file.write("")
                    printSuccess("All notes cleared.")
                except:
                    printError("Failed to clear notes.")
            else:
                printInfo("Operation cancelled.")
        else:
            printError("Invalid choice. Please select 1-4.")
        waitForEnter()
# =============================================================================
# Bonus Feature: Additional Utilities Menu
# =============================================================================
def additionalUtilities():
    """Display additional bonus features menu."""
    while True:
        clearScreen()
        printHeader("ADDITIONAL UTILITIES")
        print(Colors.GREEN + "1. Password Generator" + Colors.END)
        print(Colors.GREEN + "2. Notes Application" + Colors.END)
        print(Colors.RED + "3. Back to Main Menu" + Colors.END)
        choice = input(Colors.WHITE + "Select an option (1-3): " + Colors.END).strip()
        if choice == "3":
            break
        elif choice == "1":
            generatePassword()
        elif choice == "2":
            notesMenu()
        else:
            printError("Invalid choice. Please select 1-3.")
            waitForEnter()
# =============================================================================
# Main Application
# =============================================================================
def displayMainMenu():
    """Display the main menu of the application."""
    clearScreen()
    printHeader("COMPLETE CLI APPLICATION")
    print(Colors.GREEN + Colors.BOLD + "1. Calculator" + Colors.END)
    print(Colors.GREEN + Colors.BOLD + "2. Pattern Generator" + Colors.END)
    print(Colors.GREEN + Colors.BOLD + "3. File Handling System" + Colors.END)
    print(Colors.GREEN + Colors.BOLD + "4. Number Utilities" + Colors.END)
    print(Colors.GREEN + Colors.BOLD + "5. Simple Quiz System" + Colors.END)
    print(Colors.GREEN + Colors.BOLD + "6. Additional Utilities (Password Generator, Notes)" + Colors.END)
    print(Colors.RED + Colors.BOLD + "7. Exit Application" + Colors.END)
    print(Colors.CYAN + "=" * 60 + Colors.END)
def main():
    """Main function to run the application."""
    print(Colors.CYAN + Colors.BOLD + "Welcome to the Complete CLI Application!" + Colors.END)
    print(Colors.YELLOW + "Would you like to use the login system? (yes/no)" + Colors.END)
    useLogin = input(Colors.GREEN + "> " + Colors.END).strip().lower()
    if useLogin == "yes":
        if not loginSystem():
            return
    while True:
        displayMainMenu()
        choice = input(Colors.WHITE + "Enter your choice (1-7): " + Colors.END).strip()
        if choice == "1":
            calculatorMenu()
        elif choice == "2":
            patternMenu()
        elif choice == "3":
            fileHandlingMenu()
        elif choice == "4":
            numberUtilitiesMenu()
        elif choice == "5":
            quizMenu()
        elif choice == "6":
            additionalUtilities()
        elif choice == "7":
            clearScreen()
            printHeader("THANK YOU")
            print(Colors.GREEN + Colors.BOLD + "Thank you for using the Complete CLI Application!" + Colors.END)
            print(Colors.CYAN + Colors.BOLD + "Goodbye!" + Colors.END)
            return
        else:
            printError("Invalid choice. Please select 1-7.")
            waitForEnter()
if __name__ == "__main__":
    main()