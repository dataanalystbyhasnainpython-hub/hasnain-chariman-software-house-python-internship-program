# Multiplication Table Generator
print("********************************************")
print("WELCOME TO MULTIPLICATION TABLE GENERATOR")
print("********************************************")
print("Choose option:")
print("1. Generate single multiplication table")
print("2. Generate tables from 1 to Infinity (with bonus features)")
print()
choice = int(input("Enter your choice (1 or 2): "))
if choice == 1:
    # Single table - without bonus features
    number = int(input("Enter a number: "))
    rangevalue = int(input("Enter the range: "))
    print()
    print("Multiplication Table of", number)
    print("------------------------")
    # Using for loop for multiplication table
    for i in range(1, rangevalue + 1):
        result = number * i
        print(number, "x", i, "=", result)
    print("------------------------")
if choice == 2:
    # Tables from 1 to user's choice (infinity) - WITH bonus features
    Infinity = int(input("Enter the maximum number: "))
    rangevalue = int(input("Enter the range for each table: "))
    tablenum = 1
    # Create filename for saving all tables
    filename = "tables1to_" + str(Infinity) + ".txt"
    filecontent = ""
    # Using while loop for table numbers
    while tablenum <= Infinity:
        print()
        print("Multiplication Table of", tablenum)
        print("------------------------")
        filecontent = filecontent + "Multiplication Table of " + str(tablenum) + "\n"
        filecontent = filecontent + "------------------------\n"
        # Using for loop for multiplication table
        for i in range(1, rangevalue + 1):
            result = tablenum * i
            print(tablenum, "x", i, "=", result)
            filecontent = filecontent + str(tablenum) + " x " + str(i) + " = " + str(result) + "\n"
            # Highlight multiples of 5 or 10 with special message
            ismultiple = (result % 5 == 0) or (result % 10 == 0)
            print("-->", result, "is a multiple of 5 or 10!")
            filecontent = filecontent + "--> " + str(result) + " is a multiple of 5 or 10!\n"
        print("------------------------")
        filecontent = filecontent + "------------------------\n\n"
        tablenum = tablenum + 1
    # Save all tables to text file
    file = open(filename, "w")
    file.write(filecontent)
    file.close()
    print()
    print("All tables saved to", filename)
print()
print("Thank you for using Multiplication Table Generator!")