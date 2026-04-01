"""
Calculator Application
Python Developer Internship Task 8
A robust command line calculator with comprehensive error handling
"""
history = []
def getnumberinput(prompt):
    """
    Safely get numeric input from user with retry mechanism
    Args:
        prompt (str): The prompt message to display
    Returns:
        float: The validated number input
    """
    while True:
        try:
            userinput = input(prompt).strip()
            if not userinput:
                print("Error: Input cannot be empty. Please enter a number.")
                continue
            number = float(userinput)
            return number
        except ValueError:
            print("Error: Invalid input. Please enter a valid number.")
            continue
def getoperationchoice():
    """
    Get validated operation choice from user
    Returns:
        str: Valid operation choice
    """
    while True:
        try:
            choice = input("\nChoose an option (1 10): ").strip()
            if not choice:
                print("Error: Please enter an option.")
                continue

            if choice in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                return choice
            else:
                print("Error: Invalid option. Please choose a number between 1 and 10.")
        except Exception:
            print("Error: Unexpected error occurred. Please try again.")
            continue
def add(a, b):
    """Perform addition operation"""
    return a + b
def subtract(a, b):
    """Perform subtraction operation"""
    return a - b
def multiply(a, b):
    """Perform multiplication operation"""
    return a * b
def divide(a, b):
    """
    Perform division operation with zero division handling
    Args:
        a (float): Numerator
        b (float): Denominator
    Returns:
        float: Division result
    Raises:
        ZeroDivisionError: When denominator is zero
    """
    if b == 0:
        raise ZeroDivisionError("Division by zero is not allowed")
    return a / b
def power(a, b):
    """Perform power operation (a raised to b)"""
    result = a
    if b == 0:
        return 1
    elif b > 0:
        for i in range(1, int(b)):
            result = result * a
        return result
    else:
        return 1 / power(a, b)
def modulus(a, b):
    """
    Perform modulus operation with zero handling
    Args:
        a (float): Dividend
        b (float): Divisor
    Returns:
        float: Remainder
    Raises:
        ZeroDivisionError: When divisor is zero
    """
    if b == 0:
        raise ZeroDivisionError("Modulus by zero is not allowed")
    return a % b
def percentage(a, b):
    """
    Calculate percentage of a number
    Args:
        a (float): The number
        b (float): The percentage to calculate
    Returns:
        float: Percentage value
    """
    return (a * b) / 100
def performcalculation(operation, a, b):
    """
    Execute the selected operation with proper error handling
    Args:
        operation (function): The operation to perform
        a (float): First number
        b (float): Second number

    Returns:
        tuple: (success boolean, result or error message)
    """
    try:
        result = operation(a, b)
        if result == int(result):
            resultdisplay = int(result)
        else:
            resultdisplay = round(result, 4)
        return True, resultdisplay
    except ZeroDivisionError as e:
        return False, str(e)
    except Exception:
        return False, "Calculation error occurred"
def addtohistory(operationname, a, b, result):
    """
    Add calculation to history
    Args:
        operationname (str): Name of the operation
        a (float): First operand
        b (float): Second operand
        result (float): Result of calculation
    """
    history.append({
        "operation": operationname,
        "firstnumber": a,
        "secondnumber": b,
        "result": result
    })
def viewhistory():
    """Display calculation history"""
    if not history:
        print("\nNo calculations have been performed yet.")
        return
    print("\n" + "=" * 70)
    print("CALCULATION HISTORY".center(70))
    print("=" * 70)
    for i, entry in enumerate(history, 1):
        print(f"\nEntry {i}:")
        print(f"  Operation: {entry['operation']}")
        print(f"  Numbers: {entry['firstnumber']} and {entry['secondnumber']}")
        print(f"  Result: {entry['result']}")

    print("\n" + "=" * 70)
    print(f"Total calculations: {len(history)}")
    print("=" * 70)
def clearhistory():
    """Clear calculation history"""
    if history:
        history.clear()
        print("\nHistory cleared successfully.")
    else:
        print("\nHistory is already empty.")
def displaymenu():
    """Display the main menu in a professional format"""
    print("\n" + "=" * 50)
    print("PROFESSIONAL CALCULATOR".center(50))
    print("=" * 50)
    print("\nMAIN MENU")
    print("-" * 50)
    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")
    print("5. Power (^)")
    print("6. Modulus (| |)")
    print("7. Percentage (%)")
    print("8. View History")
    print("9. Clear History")
    print("10. Exit")
    print("-" * 50)
def runoperation(choice):
    """
    Execute the selected operation
    Args:
        choice (str): The operation choice
    """
    if choice == "1":
        operationname = "Addition"
        operationfunc = add
        needtwonumbers = True
    elif choice == "2":
        operationname = "Subtraction"
        operationfunc = subtract
        needtwonumbers = True
    elif choice == "3":
        operationname = "Multiplication"
        operationfunc = multiply
        needtwonumbers = True
    elif choice == "4":
        operationname = "Division"
        operationfunc = divide
        needtwonumbers = True
    elif choice == "5":
        operationname = "Power"
        operationfunc = power
        needtwonumbers = True
    elif choice == "6":
        operationname = "Modulus"
        operationfunc = modulus
        needtwonumbers = True
    elif choice == "7":
        operationname = "Percentage"
        operationfunc = percentage
        needtwonumbers = True
    elif choice == "8":
        viewhistory()
        return
    elif choice == "9":
        clearhistory()
        return
    elif choice == "10":
        exitcalculator()
        return

    print(f"\n {operationname.upper()} ")
    print("Please enter the numbers for calculation:")
    firstnumber = getnumberinput("First number: ")
    if operationname == "Percentage":
        secondnumber = getnumberinput("Percentage to calculate: ")
    else:
        secondnumber = getnumberinput("Second number: ")
    success, result = performcalculation(operationfunc, firstnumber, secondnumber)
    if success:
        print("\n" + "=" * 40)
        print("CALCULATION RESULT".center(40))
        print("=" * 40)
        print(f"Operation: {operationname}")
        if operationname == "Percentage":
            print(f"Input: {secondnumber}% of {firstnumber}")
        elif operationname == "Modulus":
            print(f"Input: {firstnumber} mod {secondnumber}")
        else:
            print(f"Input: {firstnumber} and {secondnumber}")
        print(f"Result: {result}")
        print("=" * 40)

        addtohistory(operationname, firstnumber, secondnumber, result)
    else:
        print("\n" + "!" * 40)
        print("ERROR".center(40))
        print("!" * 40)
        print(f"Operation: {operationname}")
        print(f"Error: {result}")
        print("!" * 40)
def exitcalculator():
    """Exit the calculator application"""
    print("\nThank you for using the Professional Calculator!")
    print(f"Total calculations performed: {len(history)}")
    exit(0)
def run():
    """
    Main application loop
    """
    print("\n" + "=" * 60)
    print("WELCOME TO PROFESSIONAL CALCULATOR".center(60))
    print("=" * 60)
    print("This calculator is designed with robust error handling")
    print("to ensure a smooth and crash free experience.")
    while True:
        try:
            displaymenu()
            choice = getoperationchoice()
            runoperation(choice)
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n\nApplication interrupted by user.")
            exitcalculator()
        except Exception:
            print("\nUnexpected error occurred. Please try again.")
if __name__ == "__main__":
    run()