import decimal
import sqlite3

from book_loans import book_loans_menu
from borrower_management import borrower_management_menu
from fines import Fines_Menu, update_all_fines
from search_books import search_books


# Helper functions for decimal tracking
def adapt_decimal(d):
  return str(d)


def convert_decimal(s):
  return decimal.Decimal(s.decode("utf-8"))


# Register the adapter and converter
sqlite3.register_adapter(decimal.Decimal, adapt_decimal)
sqlite3.register_converter("DECTEXT", convert_decimal)

# connecting to the database
conn = sqlite3.connect("library.db", detect_types=sqlite3.PARSE_DECLTYPES)

# Starting main application loop

# Initial update of all fines to simulate update on each day
update_all_fines(conn)

userInput = -1
while userInput != 0:
  # Menu Options
  print("\n\nMenu Options:")
  print("1) Search Books")
  print("2) Book Loans")
  print("3) Borrower Management")
  print("4) Fines")
  print("0) Exit")
  # TODO: Implement input validation
  userInput = int(input("Enter your menu choice: "))
  match userInput:
    case 0:  # Exit
      print("Exiting...")
    case 1:  # Search Books
      userString = input("Enter the word to search: ")
      search_books(userString, conn)
    case 2:  # Book Loans
      book_loans_menu(conn)
    case 3:  # Borrower Management
      borrower_management_menu(conn)
    case 4:  # Fines
      Fines_Menu(conn)
    case _:
      print("Invalid choice. Please input a valid option.")

conn.close()
