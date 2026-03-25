# Contact Management System - Simple File Handling Program
# File name for storing data
datafile = "contacts.txt"
# ==================== FILE INITIALIZATION ====================
def initializeFile():
    """Create the data file if it doesn't exist"""
    try:
        # Using open() to check if file exists
        file = open(datafile, "r")
        file.close()
    except FileNotFoundError:
        # Using open() with write mode to create file
        file = open(datafile, "w")
        file.write("ID|Name|Email|Phone|Address|Date\n")
        file.close()
# ==================== DISPLAY MENU ====================
def displayMenu():
    """Display the main menu options"""
    print("\n" + "=" * 50)
    print("CONTACT MANAGEMENT SYSTEM Menu")
    print("=" * 50)
    print("1. Add New Contact")
    print("2. View All Contacts")
    print("3. Search Contact")
    print("4. Delete Contact")
    print("5. Update Contact")
    print("6. Exit Program")
    print("=" * 50)
# ==================== ADD CONTACT ====================
def addContact():
    """Add a new contact to the system using append()"""
    print("\n--- ADD NEW CONTACT ---")
    # Get contact details from user
    name = input("Enter Name: ")
    if name == "":
        print("Error: Name cannot be empty!")
        return
    email = input("Enter Email: ")
    phone = input("Enter Phone: ")
    address = input("Enter Address: ")
    # Generate simple ID using current time
    import time
    currenttime = str(int(time.time()))
    contactid = currenttime[-6:]  # Last 6 digits as ID
    # Get current date and time
    currentdate = time.strftime("%Y-%m-%d %H:%M:%S")
    # Using open() with append mode to add new contact
    try:
        file = open(datafile, "a")
        file.write(contactid + "|" + name + "|" + email + "|" + phone + "|" + address + "|" + currentdate + "\n")
        file.close()
        print("\nContact added successfully!")
        print("Contact ID: " + contactid)
    except:
        print("Error: Could not save contact!")
# ==================== VIEW ALL CONTACTS ====================
def viewAllContacts():
    """Display all saved contacts using read()"""
    print("\n--- ALL CONTACTS ---")
    try:
        # Using open() with read mode
        file = open(datafile, "r")
        # Using read() to read first line (header)
        header = file.readline()
        # Using readlines() to read all remaining lines
        contacts = file.readlines()
        file.close()
        if len(contacts) == 0:
            print("No contacts found. Add some contacts first!")
            return
        # Display header
        print("\nID   |    Name        |      Email       |      Phone     |     Address")
        print("-" * 80)
        # Display each contact
        for contact in contacts:
            parts = contact.strip().split("|")
            if len(parts) >= 5:
                contactid = parts[0]
                name = parts[1]
                email = parts[2]
                phone = parts[3]
                address = parts[4]
                # Format output with proper spacing
                print(contactid.ljust(8) + name.ljust(20) + email.ljust(22) + phone.ljust(12) + address)
        print("\nTotal contacts: " + str(len(contacts)))
    except FileNotFoundError:
        print("No data file found. Please add contacts first.")
    except:
        print("Error reading contacts!")
# ==================== SEARCH CONTACT ====================
def searchContact():
    """Search for a contact by name or ID using read()"""
    print("\n--- SEARCH CONTACT ---")
    print("Search by: 1. Name | 2. ID")
    choice = input("Enter your choice (1/2): ")
    if choice != "1" and choice != "2":
        print("Error: Invalid choice!")
        return
    searchterm = input("Enter search term: ")
    if searchterm == "":
        print("Error: Search term cannot be empty!")
        return

    try:
        # Using open() with read mode
        file = open(datafile, "r")
        # Using readline() to skip header
        header = file.readline()
        # Using readlines() to get all contacts
        contacts = file.readlines()
        file.close()
        foundcontacts = []
        for contact in contacts:
            parts = contact.strip().split("|")
            if len(parts) >= 5:
                if choice == "1" and searchterm.lower() in parts[1].lower():
                    foundcontacts.append(parts)
                elif choice == "2" and searchterm == parts[0]:
                    foundcontacts.append(parts)
        if len(foundcontacts) > 0:
            print("\nFound " + str(len(foundcontacts)) + " contact(s):")
            print("\nID       Name                 Email                  Phone        Address")
            print("-" * 80)

            for contact in foundcontacts:
                print(
                    contact[0].ljust(8) + contact[1].ljust(20) + contact[2].ljust(22) + contact[3].ljust(12) + contact[
                        4])
        else:
            print("No contacts found matching your search.")

    except FileNotFoundError:
        print("No data file found. Please add contacts first.")
    except:
        print("Error searching contacts!")
# ==================== DELETE CONTACT ====================
def deleteContact():
    """Delete a contact by ID using read() and write()"""
    print("\n--- DELETE CONTACT ---")
    contactid = input("Enter Contact ID to delete: ")
    if contactid == "":
        print("Error: Contact ID cannot be empty!")
        return
    try:
        # Using open() with read mode to read all contacts
        file = open(datafile, "r")
        header = file.readline()
        contacts = file.readlines()
        file.close()
        # Find and remove the contact
        contactfound = False
        updatedcontacts = []
        for contact in contacts:
            parts = contact.strip().split("|")
            if len(parts) >= 1 and parts[0] == contactid:
                contactfound = True
                print("\nContact found: " + parts[1] + " (" + parts[0] + ")")
                confirm = input("Are you sure you want to delete this contact? (y/n): ")
                if confirm == "y" or confirm == "Y":
                    continue  # Skip adding this contact
                else:
                    updatedcontacts.append(contact)
                    print("Deletion cancelled.")
                    return
            else:
                updatedcontacts.append(contact)
        if not contactfound:
            print("No contact found with ID: " + contactid)
            return
        # Using open() with write mode to update file
        file = open(datafile, "w")
        file.write(header)
        for contact in updatedcontacts:
            file.write(contact)
        file.close()
        print("Contact deleted successfully!")
    except FileNotFoundError:
        print("No data file found. Please add contacts first.")
    except:
        print("Error deleting contact!")

# ==================== UPDATE CONTACT ====================
def updateContact():
    """Update an existing contact using read() and write()"""
    print("\n--- UPDATE CONTACT ---")
    contactid = input("Enter Contact ID to update: ")
    if contactid == "":
        print("Error: Contact ID cannot be empty!")
        return
    try:
        # Using open() with read mode to read all contacts
        file = open(datafile, "r")
        header = file.readline()
        contacts = file.readlines()
        file.close()
        # Find and update the contact
        contactfound = False
        updatedcontacts = []
        for contact in contacts:
            parts = contact.strip().split("|")
            if len(parts) >= 5 and parts[0] == contactid:
                contactfound = True
                print("\nEditing contact: " + parts[1])
                print("Leave field empty to keep current value")
                print("-" * 40)
                # Show current values and get new values
                print("Current Name: " + parts[1])
                newname = input("New Name: ")
                print("Current Email: " + parts[2])
                newemail = input("New Email: ")
                print("Current Phone: " + parts[3])
                newphone = input("New Phone: ")
                print("Current Address: " + parts[4])
                newaddress = input("New Address: ")
                # Update with new values or keep old ones
                if newname == "":
                    newname = parts[1]
                if newemail == "":
                    newemail = parts[2]
                if newphone == "":
                    newphone = parts[3]
                if newaddress == "":
                    newaddress = parts[4]
                # Keep the original date
                if len(parts) >= 6:
                    createddate = parts[5]
                else:
                    import time
                    createddate = time.strftime("%Y-%m-%d %H:%M:%S")
                # Create updated contact
                updatedcontact = contactid + "|" + newname + "|" + newemail + "|" + newphone + "|" + newaddress + "|" + createddate + "\n"
                updatedcontacts.append(updatedcontact)
                print("\nContact updated successfully!")
            else:
                updatedcontacts.append(contact)
        if not contactfound:
            print("No contact found with ID: " + contactid)
            return
        # Using open() with write mode to update file
        file = open(datafile, "w")
        file.write(header)
        for contact in updatedcontacts:
            file.write(contact)
        file.close()
    except FileNotFoundError:
        print("No data file found. Please add contacts first.")
    except:
        print("Error updating contact!")
# ==================== MAIN PROGRAM ====================
def main():
    """Main program loop"""
    # Initialize the data file
    initializeFile()
    print("\n" + "=" * 50)
    print("WELCOME TO CONTACT MANAGEMENT SYSTEM")
    print("=" * 50)
    # Main program loop
    while True:
        displayMenu()
        choice = input("\nEnter your choice (1-6): ")
        if choice == "1":
            addContact()
        elif choice == "2":
            viewAllContacts()
        elif choice == "3":
            searchContact()
        elif choice == "4":
            deleteContact()
        elif choice == "5":
            updateContact()
        elif choice == "6":
            print("\n" + "=" * 50)
            print("Thank you for using Contact Management System!")
            print("Goodbye!")
            print("=" * 50)
            break
        else:
            print("\nInvalid choice! Please enter a number between 1 and 6.")
        # Pause before showing menu again
        input("\nPress Enter to continue...")
# Run the program
main()