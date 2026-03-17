# task 2 operators
print("=" * 50)
print("      WELCOME TO THE NUMBER ANALYZER PROGRAM")
print("=" * 50)
# List to store all analyzed numbers (for bonus feature)
analyzednumbers = []
while True:
    try:
        print("\n" + "-" * 30)
        user_input = input("Enter a number (or 'quit' to exit): ")
        # Check if user wants to quit
        if user_input.lower() == 'quit':
            break
        # Convert input to integer
        number = int(user_input)
        # Add number to our list
        analyzednumbers.append(number)
        print("\n" + "=" * 30)
        print("      ANALYSIS RESULTS")
        print("=" * 30)
        # Whether Positive, Negative, or Zero
        print("\nWhether Positive, Negative, or Zero:")
        if number > 0:
            print(" Whether The number is POSITIVE")
        elif number < 0:
            print(" Whether The number is NEGATIVE")
        else:
            print("The number is ZERO")
        # Whether Even or Odd
        print("\nWhether Even or Odd:")
        if number == 0:
            print(" Whether number Zero is neither even nor odd")
        elif number % 2 == 0:
            print("Whether number is EVEN")
        else:
            print("Whether number is ODD")
        # Whether Divisible by both 3 and 5
        print("\nWhether Divisible by both 3 and 5:")
        if number % 3 == 0 and number % 5 == 0:
            print("YES, Whether the number is divisible by both 3 and 5")
        else:
            print("NO, Whether the number is NOT divisible by both 3 and 5")
        # Whether Within range 1-100
        print("\nWhether number Within range 1-100:")
        if number >= 1 and number <= 100:
            print("YES, the number is within the range 1-100")
        else:
            print("NO, Whether number is NOT within the range 1-100")
        # SPECIAL CONDITION: Positive AND Even AND Within Range
        print("\n[SPECIAL CHECK] Whether Multiple conditions:")
        if number > 0 and number % 2 == 0 and number >= 1 and number <= 100:
            print("SPECIAL CONDITION MATCHED!")
            print("Whether number is positive, even, AND within 1-100 range")
        else:
            print("No special condition matched")
        # DEMONSTRATING LOGICAL OPERATORS
        print("\n" + "=" * 30)
        print("   LOGICAL OPERATORS IN ACTION")
        print("=" * 30)
        # Using 'and' operator
        print("\nUsing 'and' operator:")
        if number > 0 and number < 50:
            print(" Whether Number is positive AND less than 50")
        # Using 'or' operator
        print("\nUsing 'or' operator:")
        if number < 0 or number > 100:
            print(" Whether Number is either negative OR greater than 100")
        # Using 'not' operator
        print("\nUsing 'not' operator:")
        if not (number % 2 == 0):
            print("Whether Number is NOT even (it's odd)")
        print("\n" + "=" * 30)
    except ValueError:
        print("Invalid input! Please enter a valid number.")
# Display summary
print("\n" + "=" * 50)
print("           SUMMARY REPORT")
print("=" * 50)
if len(analyzednumbers) > 0:
    print(f"\nTotal numbers analyzed: {len(analyzednumbers)}")
    print(f"Numbers entered: {analyzednumbers}")
    # Count statistics
    positive = 0
    negative = 0
    zero = 0
    special = 0
    for num in analyzednumbers:
        if num > 0:
            positive = positive + 1
        elif num < 0:
            negative = negative + 1
        else:
            zero = zero + 1
        if num > 0 and num % 2 == 0 and num >= 1 and num <= 100:
            special = special + 1
    print(f"\nStatistics:")
    print(f"  • Positive numbers: {positive}")
    print(f"  • Negative numbers: {negative}")
    print(f"  • Zero: {zero}")
    if special > 0:
        print(f"\nSpecial condition matches: {special}")
else:
    print("\nNo numbers were analyzed.")
print("\n" + "=" * 50)
print("      THANK YOU FOR USING THE NUMBER ANALYZER!")
print("=" * 50)