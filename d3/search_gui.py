import tkinter as tk
from tkinter import messagebox, ttk

from search_books import search_books


# Simple GUI for searching books in the library DB.
# Probably not perfect but gets the job done.
class SearchGUI:
  def __init__(self, master, conn):
    self.master = master
    self.master.title("Library Book Search")
    self.conn = conn

    # Search bar frame
    search_frame = tk.Frame(master)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Search Books: ").pack(side=tk.LEFT)

    # User types search keyword here
    self.search_entry = ttk.Entry(search_frame, width=60)
    self.search_entry.bind("<Return>", self.perform_search_event)
    self.search_entry.pack(side=tk.LEFT, padx=5)

    # Button to actually run search
    self.search_button = ttk.Button(
      search_frame, text="Search", command=self.perform_search
    ).pack(side=tk.LEFT)

    # Set up results table
    columns = ("ISBN", "Title", "Authors", "Status", "BorrowerID")
    self.tree = ttk.Treeview(master, columns=columns, show="headings", height=12)

    # Set headings
    for col in columns:
      self.tree.heading(col, text=col)
      # wider column for title so it doesn’t look squished
      self.tree.column(col, width=800 if col == "Title" else 160)

    self.tree.pack(pady=10)

  def perform_search_event(self, event):
    self.perform_search()

  # Runs whenever the user clicks "Search"
  def perform_search(self):
    keyword = self.search_entry.get().strip()

    # Clear old rows from the table
    for row in self.tree.get_children():
      self.tree.delete(row)

    if keyword == "":
      messagebox.showwarning("Input Required", "Please enter a search term.")
      return

    # Call the provided search function
    results = search_books(keyword, self.conn)

    if not results:
      messagebox.showinfo("No Results", f"No matches found for '{keyword}'.")
      return

    # Need borrower IDs because search_books doesn't return them
    borrower_map = self.get_borrower_map()

    # Insert each row into the table
    for isbn, title, authors, status in results:
      borrower_id = borrower_map.get(isbn, "NULL")
      self.tree.insert("", tk.END, values=(isbn, title, authors, status, borrower_id))

  # Builds a map of ISBN → BorrowerID (or NULL)
  def get_borrower_map(self):
    cursor = self.conn.cursor()
    cursor.execute("""
            SELECT Isbn, Card_id
            FROM BOOK_LOANS
            WHERE Date_in IS NULL
        """)
    rows = cursor.fetchall()

    # Convert to dictionary for easier lookup
    borrower_dict = {}
    for isbn, card_id in rows:
      borrower_dict[isbn] = card_id if card_id else "NULL"

    return borrower_dict


# Launches the GUI when called
def start_search_gui(conn):
  root = tk.Tk()
  SearchGUI(root, conn)
  root.mainloop()
