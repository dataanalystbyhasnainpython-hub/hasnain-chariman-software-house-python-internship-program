"""
Secure Login System with Error Handling
Task: Build a login system with 3 attempts, input validation, and error handling.
"""

import getpass

VALIDCREDENTIALS = {
    "intern2026": "HK@1234",
    "admin": "flask",
    "developer": "hasnain python developer"
}
MAXATTEMPTS = 3
LOGFILENAME = "loginattempts.log"
logfile = open(LOGFILENAME, "a")
print("=" * 40)
print("     SECURE LOGIN SYSTEM")
print("=" * 40)
attemptcount = 0
while attemptcount < MAXATTEMPTS:
    try:
        usernameinput = input("\nEnter username: ").strip()
        passwordinput = input("Enter password: ").strip()
        if not usernameinput or not passwordinput:
            print("\nERROR: Username and password cannot be empty.")
            attemptcount += 1
            logfile.write(f"User: EMPTY | Success: False | Empty input\n")
            logfile.flush()
            if attemptcount == MAXATTEMPTS:
                print("\nLOCKED: Maximum attempts reached. System locked!")
                logfile.write(f"System locked due to empty input\n")
            continue
        if usernameinput in VALIDCREDENTIALS and VALIDCREDENTIALS[usernameinput] == passwordinput:
            print("\n" + "=" * 40)
            print(f"SUCCESS: Login successful! Welcome {usernameinput}.")
            print("=" * 40)
            logfile.write(f"User: {usernameinput} | Success: True | Login successful\n")
            logfile.flush()
            break
        else:
            attemptcount += 1
            remaining = MAXATTEMPTS - attemptcount
            print(f"\nERROR: Invalid credentials! You have {remaining} attempts left.")
            logfile.write(f"User: {usernameinput} | Success: False | Invalid credentials\n")
            logfile.flush()
            if attemptcount == MAXATTEMPTS:
                print("\nLOCKED: Maximum attempts reached. System locked!")
                logfile.write(f"System locked after {MAXATTEMPTS} failed attempts\n")
                logfile.flush()
    except Exception as e:
        attemptcount += 1
        print(f"\nERROR: Something went wrong - {str(e)}")
        logfile.flush()
        if attemptcount == MAXATTEMPTS:
            print("\nLOCKED: System locked due to errors!")
logfile.close()
print("\nLogin attempts logged to 'loginattempts.log'")