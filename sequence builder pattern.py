# Patterns and Sequence Builder
#usingANSI escape codes.
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
BOLD = '\033[1m'
END = '\033[0m'
#Main program code According to Required pattern shapes
def showStarTriangle(size):
    print(BOLD + GREEN + "\nStar Triangle Pattern:" + END)
    print(CYAN + "~" * 40 + END)
    for i in range(1, size + 1):
        print(BLUE + "*" * i + END)
    for i in range(size - 1, 0, -1):
        print(CYAN + "*" * i + END)
    print(CYAN + "~" * 40 + END)
def showReverseStar(size):
    print(BOLD + GREEN + "\nReverse Star Pattern:" + END)
    print(CYAN + "~" * 40 + END)
    for i in range(size, 0, -1):
        print(MAGENTA + "*" * i + END)
    for i in range(2, size + 1):
        print(MAGENTA + "*" * i + END)
    print(CYAN + "~" * 40 + END)
def showNumberTriangle(size):
    print(BOLD + GREEN + "\nNumber Triangle Pattern:" + END)
    print(CYAN + "~" * 40 + END)
    for i in range(1, size + 1):
        for j in range(1, i + 1):
            print(YELLOW + str(j) + END, end="")
        print()
    print(CYAN + "~" * 40 + END)
def showNumberPyramid(size):
    print(BOLD + GREEN + "\nNumber Pyramid Pattern:" + END)
    print(CYAN + "~" * 40 + END)
    for i in range(1, size + 1):
        print(" " * (size - i), end="")
        for j in range(1, i + 1):
            print(YELLOW + str(j) + END, end="")
        for j in range(i - 1, 0, -1):
            print(YELLOW + str(j) + END, end="")
        print()
    print(CYAN + "~" * 40 + END)
print("\n" + "=" * 50)
print(BOLD + CYAN + "PATTERN BUILDER" + END)
print("=" * 50)
while True:
    print("\n" + BOLD + YELLOW + "Patterns:" + END)
    print("1. Star Triangle")
    print("2. Reverse Star")
    print("3. Number Triangle")
    print("4. Number Pyramid")
    print("0. Exit")
    choice = input("\nEnter choice 0-4: ")
    if choice == "0":
        print("\n" + GREEN + "Goodbye!" + END)
        break
    if choice not in ["1", "2", "3", "4"]:
        print(RED + "Invalid choice" + END)
        continue
    sizeInput = input("Enter size: ")
    if not sizeInput.isdigit():
        print(RED + "Invalid size" + END)
        continue
    size = int(sizeInput)
    if size <= 0:
        print(RED + "Size must be positive" + END)
        continue
    if choice == "1":
        showStarTriangle(size)
    elif choice == "2":
        showReverseStar(size)
    elif choice == "3":
        showNumberTriangle(size)
    elif choice == "4":
        showNumberPyramid(size)
    print(GREEN + "Pattern generated!" + END)
    again = input("\nAnother pattern? (y/n): ")
    if again.lower() != "y":
        print("\n" + GREEN + "Goodbye!" + END)
        break
