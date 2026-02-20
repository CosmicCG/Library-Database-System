import decimal
import sqlite3
import tkinter as tk
from tkinter import ttk

from book_loans_gui import start_book_loans_gui
from borrower_gui import start_borrower_gui
from fines import update_all_fines
from fines_gui import start_fines_gui
from search_gui import start_search_gui

# from search_books import search_books


# Menu Helper Functions
def quit_tk():
  root.destroy()
  quit()


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


# Initial update of all fines to simulate update on each day
update_all_fines(conn)

# Main Menu
root = tk.Tk()
root.title("Library Management System")

root.geometry("600x400")
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)


search_button = ttk.Button(root)
search_button["text"] = "Search Books"
search_button["command"] = lambda: start_search_gui(conn)
search_button.grid(row=0, column=0, sticky="nsew")

book_loans_button = ttk.Button(root)
book_loans_button["text"] = "Book Loans"
book_loans_button["command"] = lambda: start_book_loans_gui(conn)
book_loans_button.grid(row=0, column=1, sticky="nsew")

borrower_management_button = ttk.Button(root)
borrower_management_button["text"] = "Borrower Management"
borrower_management_button["command"] = lambda: start_borrower_gui(conn)
borrower_management_button.grid(row=1, column=0, sticky="nsew")

fines_button = ttk.Button(root)
fines_button["text"] = "Fines"
fines_button["command"] = lambda: start_fines_gui(conn)
fines_button.grid(row=1, column=1, sticky="nsew")

exit_button = ttk.Button(root)
exit_button["text"] = "Exit"
exit_button["command"] = quit_tk
exit_button.grid(row=2, column=0, sticky="nsew", columnspan=2)

# keep the window dispalying
try:
  from ctypes import windll

  windll.shcore.SetProcessDpiAwareness(1)
finally:
  root.mainloop()

conn.close()
