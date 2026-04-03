"""
Library Management System
A commandline application demonstrating ObjectOriented Programming concepts
Task 9 Python Developer Internship
"""
class Book:
    """Represents a single book in the library system."""
    def __init__(self, bookid, title, author):
        self.bookid = bookid
        self.title = title
        self.author = author
        self.status = "Available"
        self.issuedto = None
    def getbriefinfo(self):
        return f"ID: {self.bookid:<8} | Title: {self.title:<30} | Author: {self.author:<20} | Status: {self.status}"
    def getdetailedinfo(self):
        borderline = "=" * 60
        details = f"""
{borderline}
BOOK DETAILS
{borderline}
Book ID:     {self.bookid}
Title:       {self.title}
Author:      {self.author}
Status:      {self.status}
"""
        if self.issuedto:
            details += f"Issued To:   {self.issuedto}\n"
        details += borderline
        return details
    def isavailable(self):
        return self.status == "Available"
    def issue(self, membername):
        if not self.isavailable():
            return False
        self.status = "Issued"
        self.issuedto = membername
        return True
    def returnbook(self):
        if self.isavailable():
            return False
        self.status = "Available"
        self.issuedto = None
        return True
class Library:
    """Manages the collection of books and all library operations."""
    def __init__(self):
        self.books = []
    def isbookidexists(self, bookid):
        for book in self.books:
            if book.bookid == bookid:
                return True
        return False
    def findbookbyid(self, bookid):
        for book in self.books:
            if book.bookid == bookid:
                return book
        return None
    def addbook(self, bookid, title, author):
        if not bookid or not title or not author:
            print("\n[ERROR] All fields are required. Please try again.")
            return False
        if self.isbookidexists(bookid):
            print(f"\n[ERROR] A book with ID '{bookid}' already exists.")
            return False
        newbook = Book(bookid, title.strip(), author.strip())
        self.books.append(newbook)
        print(f"\n[SUCCESS] Book '{title}' has been added to the library.")
        return True
    def viewallbooks(self):
        if not self.books:
            print("\n" + "=" * 80)
            print(" " * 25 + "LIBRARY CATALOG")
            print("=" * 80)
            print("\nThe library is empty. No books to display.")
            print("=" * 80)
            return
        print("\n" + "=" * 80)
        print(" " * 30 + "LIBRARY CATALOG")
        print("=" * 80)
        for index, book in enumerate(self.books, 1):
            print(f"\n{index:2d}. {book.getbriefinfo()}")
        print("\n" + "=" * 80)
        print(f"TOTAL BOOKS IN LIBRARY: {len(self.books)}")
        print("=" * 80)
    def searchbook(self, searchterm):
        if not searchterm:
            print("\n[ERROR] Please provide a search term.")
            return []
        searchtermlower = searchterm.lower().strip()
        matchingbooks = []
        for book in self.books:
            if searchtermlower in book.title.lower() or searchtermlower == book.bookid.lower():
                matchingbooks.append(book)
        print("\n" + "=" * 80)
        print(f"SEARCH RESULTS FOR: '{searchterm}'")
        print("=" * 80)
        if not matchingbooks:
            print("\nNo books found matching your search criteria.")
        else:
            print(f"\nFound {len(matchingbooks)} book(s):")
            for index, book in enumerate(matchingbooks, 1):
                print(f"\n{index}. {book.getbriefinfo()}")
                if len(matchingbooks) == 1:
                    print(book.getdetailedinfo())
        print("=" * 80)
        return matchingbooks
    def removebook(self, bookid):
        if not bookid:
            print("\n[ERROR] Please provide a book ID.")
            return False
        book = self.findbookbyid(bookid)
        if not book:
            print(f"\n[ERROR] No book found with ID '{bookid}'.")
            return False
        if not book.isavailable():
            print(f"\n[ERROR] Cannot remove '{book.title}' because it is currently issued to {book.issuedto}.")
            print("        Please return the book before removing it.")
            return False
        self.books.remove(book)
        print(f"\n[SUCCESS] Book '{book.title}' (ID: {bookid}) has been removed from the library.")
        return True
    def issuebook(self, bookid, membername):
        if not bookid or not membername:
            print("\n[ERROR] Both Book ID and Member Name are required.")
            return False
        book = self.findbookbyid(bookid)
        if not book:
            print(f"\n[ERROR] No book found with ID '{bookid}'.")
            return False
        if not book.isavailable():
            print(f"\n[ERROR] '{book.title}' is already issued to {book.issuedto}.")
            return False
        if book.issue(membername):
            print(f"\n[SUCCESS] '{book.title}' has been issued to {membername}.")
            return True
        return False
    def returnbook(self, bookid):
        if not bookid:
            print("\n[ERROR] Please provide a book ID.")
            return False
        book = self.findbookbyid(bookid)
        if not book:
            print(f"\n[ERROR] No book found with ID '{bookid}'.")
            return False
        if book.isavailable():
            print(f"\n[ERROR] '{book.title}' is not currently issued. It is already available.")
            return False
        if book.returnbook():
            print(f"\n[SUCCESS] '{book.title}' has been returned to the library.")
            return True
        return False
    def getstatistics(self):
        totalbooks = len(self.books)
        availablebooks = 0
        issuedbooks = 0
        for book in self.books:
            if book.isavailable():
                availablebooks += 1
            else:
                issuedbooks += 1

        return {
            "total": totalbooks,
            "available": availablebooks,
            "issued": issuedbooks
        }
    def displaystatistics(self):
        stats = self.getstatistics()
        print("\n" + "=" * 60)
        print(" " * 20 + "LIBRARY STATISTICS")
        print("=" * 60)
        print(f"\nTotal Books:          {stats['total']}")
        print(f"Available Books:      {stats['available']}")
        print(f"Issued Books:         {stats['issued']}")
        if stats['total'] > 0:
            usagerate = (stats['issued'] / stats['total']) * 100
            print(f"Library Usage Rate:    {usagerate:.1f}%")
        print("\n" + "=" * 60)
class MenuManager:
    """Handles all menu display and user interaction."""
    @staticmethod
    def displaymainmenu():
        print("\n" + "=" * 55)
        print("     LIBRARY Book MANAGEMENT SYSTEM")
        print("=" * 55)
        print("\nMAIN MENU:")
        print("-" * 55)
        print("1.  Add a New Book")
        print("2.  View All Books")
        print("3.  Search for a Book")
        print("4.  Remove a Book")
        print("5.  Issue a Book")
        print("6.  Return a Book")
        print("7.  View Library Statistics")
        print("8.  Exit System")
        print("-" * 55)
    @staticmethod
    def getuserchoice():
        try:
            choice = int(input("\nEnter your choice (1-8): "))
            if 1 <= choice <= 8:
                return choice
            else:
                print("\n[ERROR] Please enter a number between 1 and 8.")
                return None
        except ValueError:
            print("\n[ERROR] Invalid input. Please enter a number.")
            return None
    @staticmethod
    def pausescreen():
        input("\nPress Enter to continue...")
    @staticmethod
    def getbookdetails():
        print("\n--- ADD NEW BOOK ---")
        print("-" * 30)
        bookid = input("Enter Book ID: ").strip()
        title = input("Enter Book Title: ").strip()
        author = input("Enter Book Author: ").strip()
        return bookid, title, author
    @staticmethod
    def getsearchterm():
        print("\n--- SEARCH BOOK ---")
        print("-" * 30)
        return input("Enter Book Title or ID to search: ").strip()
    @staticmethod
    def getbookid(purpose):
        print(f"\n--- {purpose} ---")
        print("-" * 30)
        return input("Enter Book ID: ").strip()
    @staticmethod
    def getmembername():
        return input("Enter Member Name: ").strip()
class LibrarySystem:
    """Main controller class that orchestrates the entire library system."""
    def __init__(self):
        self.library = Library()
        self.menu = MenuManager()
        self.isrunning = True
    def run(self):
        self.displaywelcomemessage()
        while self.isrunning:
            self.menu.displaymainmenu()
            choice = self.menu.getuserchoice()
            if choice is None:
                self.menu.pausescreen()
                continue
            self.processchoice(choice)
            if choice != 8:
                self.menu.pausescreen()
    def displaywelcomemessage(self):
        print("\n" + "=" * 60)
        print("     WELCOME TO THE LIBRARY Book MANAGEMENT SYSTEM")
        print("=" * 60)
        print("\nSystem initialized successfully!")
        print("Ready to manage your library...")
    def processchoice(self, choice):
        if choice == 1:
            self.handleaddbook()
        elif choice == 2:
            self.handleviewbooks()
        elif choice == 3:
            self.handlesearchbook()
        elif choice == 4:
            self.handleremovebook()
        elif choice == 5:
            self.handleissuebook()
        elif choice == 6:
            self.handlereturnbook()
        elif choice == 7:
            self.handleviewstatistics()
        elif choice == 8:
            self.handleexit()
    def handleaddbook(self):
        bookid, title, author = self.menu.getbookdetails()
        self.library.addbook(bookid, title, author)
    def handleviewbooks(self):
        self.library.viewallbooks()
    def handlesearchbook(self):
        searchterm = self.menu.getsearchterm()
        if searchterm:
            self.library.searchbook(searchterm)
    def handleremovebook(self):
        bookid = self.menu.getbookid("REMOVE BOOK")
        if bookid:
            self.library.removebook(bookid)
    def handleissuebook(self):
        bookid = self.menu.getbookid("ISSUE BOOK")
        if bookid:
            membername = self.menu.getmembername()
            self.library.issuebook(bookid, membername)
    def handlereturnbook(self):
        bookid = self.menu.getbookid("RETURN BOOK")
        if bookid:
            self.library.returnbook(bookid)
    def handleviewstatistics(self):
        self.library.displaystatistics()
    def handleexit(self):
        print("\n" + "=" * 60)
        print("     THANK YOU FOR USING THE LIBRARY SYSTEM")
        print("=" * 60)
        print("\nGoodbye!")
        self.isrunning = False
def main():
    """Main entry point of the application."""
    system = LibrarySystem()
    system.run()
if __name__ == "__main__":
    main()