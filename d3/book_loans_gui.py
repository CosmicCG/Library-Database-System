import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from book_loans import checkin, checkout, search_loans
from search_books import search_books


class BookLoansGUI:
  def __init__(self, master, conn):
    self.master = master
    self.master.title("Book Loans Management")
    self.master.geometry("1200x800")
    self.conn = conn

    # Create notebook for tabs
    self.notebook = ttk.Notebook(master)
    self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Create two tabs
    self.checkout_tab = tk.Frame(self.notebook)
    self.checkin_tab = tk.Frame(self.notebook)

    self.notebook.add(self.checkout_tab, text="Check Out Books")
    self.notebook.add(self.checkin_tab, text="Check In Books")

    # Set up both tabs
    self.setup_checkout_tab()
    self.setup_checkin_tab()

  def setup_checkout_tab(self):
    """Set up the Check Out Books tab."""
    # Title
    tk.Label(
      self.checkout_tab, text="Check Out Books", font=("Arial", 14, "bold")
    ).pack(pady=10)

    # Instructions
    tk.Label(
      self.checkout_tab,
      text="You can checkout books by entering ISBN directly, or search and select from results.",
      font=("Arial", 9),
      fg="gray",
    ).pack(pady=5)

    # Create two sections: Direct ISBN and Search
    # Section 1: Checkout by ISBN directly
    direct_frame = tk.LabelFrame(
      self.checkout_tab, text="Checkout by ISBN", font=("Arial", 10, "bold")
    )
    direct_frame.pack(fill="x", padx=20, pady=10)

    isbn_frame = tk.Frame(direct_frame)
    isbn_frame.pack(pady=10)

    tk.Label(isbn_frame, text="ISBN:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    self.isbn_entry = ttk.Entry(isbn_frame, width=30)
    self.isbn_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(isbn_frame, text="Borrower Card ID:").grid(
      row=0, column=2, padx=5, pady=5, sticky="e"
    )
    self.card_id_entry = ttk.Entry(isbn_frame, width=30)
    self.card_id_entry.grid(row=0, column=3, padx=5, pady=5)

    ttk.Button(isbn_frame, text="Check Out", command=self.checkout_by_isbn).grid(
      row=0, column=4, padx=10, pady=5
    )

    # Separator
    tk.Label(self.checkout_tab, text="OR", font=("Arial", 12, "bold")).pack(pady=10)

    # Section 2: Search and select books
    search_frame = tk.LabelFrame(
      self.checkout_tab, text="Search and Select Books", font=("Arial", 10, "bold")
    )
    search_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Search bar
    search_bar_frame = tk.Frame(search_frame)
    search_bar_frame.pack(pady=10)

    tk.Label(search_bar_frame, text="Search Books:").pack(side=tk.LEFT, padx=5)
    self.book_search_entry = ttk.Entry(search_bar_frame, width=50)
    self.book_search_entry.bind("<Return>", lambda e: self.search_books_for_checkout())
    self.book_search_entry.pack(side=tk.LEFT, padx=5)

    ttk.Button(
      search_bar_frame,
      text="Search",
      command=self.search_books_for_checkout,
    ).pack(side=tk.LEFT, padx=5)

    # Book results table
    columns = ("ISBN", "Title", "Authors", "Status")
    self.book_tree = ttk.Treeview(
      search_frame, columns=columns, show="headings", height=10, selectmode="extended"
    )

    # Set headings and column widths
    self.book_tree.heading("ISBN", text="ISBN")
    self.book_tree.heading("Title", text="Title")
    self.book_tree.heading("Authors", text="Authors")
    self.book_tree.heading("Status", text="Status")

    self.book_tree.column("ISBN", width=120)
    self.book_tree.column("Title", width=400)
    self.book_tree.column("Authors", width=250)
    self.book_tree.column("Status", width=80)

    # Scrollbar for book tree
    book_scrollbar = ttk.Scrollbar(
      search_frame, orient="vertical", command=self.book_tree.yview
    )
    self.book_tree.configure(yscrollcommand=book_scrollbar.set)

    self.book_tree.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
    book_scrollbar.pack(side=tk.RIGHT, fill="y", pady=5)

    # Selected books frame
    selected_frame = tk.Frame(search_frame)
    selected_frame.pack(fill="x", padx=5, pady=5)

    tk.Label(selected_frame, text="Borrower Card ID:").pack(side=tk.LEFT, padx=5)
    self.selected_card_id_entry = ttk.Entry(selected_frame, width=30)
    self.selected_card_id_entry.pack(side=tk.LEFT, padx=5)

    self.selected_count_label = tk.Label(selected_frame, text="Selected: 0", fg="blue")
    self.selected_count_label.pack(side=tk.LEFT, padx=5)

    ttk.Button(
      selected_frame,
      text="Check Out Selected",
      command=self.checkout_selected_books,
    ).pack(side=tk.LEFT, padx=10)

    # Update selection count when treeview selection changes
    self.book_tree.bind("<<TreeviewSelect>>", self.update_selection_count)

    # Info label
    info_label = tk.Label(
      search_frame,
      text="Tip: Use Ctrl+Click or Shift+Click to select multiple books. Green = Available, Red = Checked Out",
      font=("Arial", 8),
      fg="gray",
    )
    info_label.pack(pady=5)

  def setup_checkin_tab(self):
    """Set up the Check In Books tab."""
    # Title
    tk.Label(self.checkin_tab, text="Check In Books", font=("Arial", 14, "bold")).pack(
      pady=10
    )

    # Instructions
    tk.Label(
      self.checkin_tab,
      text="Search for loans by ISBN, Borrower Card ID, or Borrower Name. Select loans to check in (max 3 at once).",
      font=("Arial", 9),
      fg="gray",
    ).pack(pady=5)

    # Search frame
    search_frame = tk.LabelFrame(
      self.checkin_tab, text="Search Loans", font=("Arial", 10, "bold")
    )
    search_frame.pack(fill="x", padx=20, pady=10)

    search_bar_frame = tk.Frame(search_frame)
    search_bar_frame.pack(pady=10)

    tk.Label(search_bar_frame, text="Search by ISBN, Card ID, or Borrower Name:").pack(
      side=tk.LEFT, padx=5
    )
    self.loan_search_entry = ttk.Entry(search_bar_frame, width=50)
    self.loan_search_entry.bind("<Return>", lambda e: self.search_loans_for_checkin())
    self.loan_search_entry.pack(side=tk.LEFT, padx=5)

    ttk.Button(
      search_bar_frame, text="Search", command=self.search_loans_for_checkin
    ).pack(side=tk.LEFT, padx=5)

    # Loan results table
    columns = (
      "Loan ID",
      "ISBN",
      "Title",
      "Card ID",
      "Borrower",
      "Date Out",
      "Due Date",
      "Status",
    )
    self.loan_tree = ttk.Treeview(
      search_frame, columns=columns, show="headings", height=12, selectmode="extended"
    )

    # Set headings and column widths
    for col in columns:
      self.loan_tree.heading(col, text=col)
      if col == "Title":
        self.loan_tree.column(col, width=300)
      elif col == "Borrower":
        self.loan_tree.column(col, width=150)
      elif col in ("Date Out", "Due Date"):
        self.loan_tree.column(col, width=100)
      else:
        self.loan_tree.column(col, width=100)

    # Scrollbar for loan tree
    loan_scrollbar = ttk.Scrollbar(
      search_frame, orient="vertical", command=self.loan_tree.yview
    )
    self.loan_tree.configure(yscrollcommand=loan_scrollbar.set)

    self.loan_tree.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
    loan_scrollbar.pack(side=tk.RIGHT, fill="y", pady=5)

    # Check in button frame
    checkin_frame = tk.Frame(self.checkin_tab)
    checkin_frame.pack(pady=10)

    ttk.Button(
      checkin_frame, text="Check In Selected", command=self.checkin_selected_loans
    ).pack(padx=10)

    # Result count label
    self.checkin_result_label = tk.Label(checkin_frame, text="", font=("Arial", 9))
    self.checkin_result_label.pack(pady=5)

    # Info label
    info_label = tk.Label(
      checkin_frame,
      text="Tip: Use Ctrl+Click or Shift+Click to select multiple loans (max 3). Yellow = Out, Gray = Already In",
      font=("Arial", 8),
      fg="gray",
    )
    info_label.pack(pady=5)

    # Store loan data
    self.loan_data = []

  def checkout_by_isbn(self):
    """Check out a book using direct ISBN entry."""
    isbn = self.isbn_entry.get().strip()
    card_id = self.card_id_entry.get().strip()

    if not isbn:
      messagebox.showerror("Error", "Please enter an ISBN.", parent=self.master)
      return

    if not card_id:
      messagebox.showerror(
        "Error", "Please enter a Borrower Card ID.", parent=self.master
      )
      return

    # Use the checkout function from book_loans.py
    # We need to capture errors, so let's create a wrapper
    result = self.perform_checkout(isbn, card_id)

    if result["success"]:
      messagebox.showinfo("Success", result["message"], parent=self.master)
      # Clear entries
      self.isbn_entry.delete(0, tk.END)
      self.card_id_entry.delete(0, tk.END)
    else:
      messagebox.showerror("Error", result["message"], parent=self.master)

  def search_books_for_checkout(self):
    """Search for books and display in the table."""
    keyword = self.book_search_entry.get().strip()

    if not keyword:
      messagebox.showwarning(
        "Input Required", "Please enter a search term.", parent=self.master
      )
      return

    # Clear old rows
    for row in self.book_tree.get_children():
      self.book_tree.delete(row)

    # Search books
    results = search_books(keyword, self.conn)

    if not results:
      messagebox.showinfo(
        "No Results", f"No matches found for '{keyword}'.", parent=self.master
      )
      return

    # Insert results into tree
    for isbn, title, authors, status in results:
      # Only show books that are available (Status = 'IN')
      if status == "IN":
        self.book_tree.insert(
          "", tk.END, values=(isbn, title, authors, status), tags=("available",)
        )
      else:
        self.book_tree.insert(
          "", tk.END, values=(isbn, title, authors, status), tags=("checked_out",)
        )

    # Configure tags for styling
    self.book_tree.tag_configure("available", background="lightgreen")
    self.book_tree.tag_configure("checked_out", background="lightcoral")

    # Enable selection - treeview already supports multiple selection with Ctrl/Shift

  def get_selected_books(self):
    """Get currently selected books from the treeview."""
    selection = self.book_tree.selection()
    selected_isbns = []
    for item_id in selection:
      item = self.book_tree.item(item_id)
      isbn = item["values"][0]
      status = item["values"][3]
      if status == "IN":
        selected_isbns.append(isbn)
    return selected_isbns

  def update_selection_count(self, event=None):
    """Update the selection count label."""
    selected_isbns = self.get_selected_books()
    count = len(selected_isbns)
    self.selected_count_label.config(text=f"Selected: {count}")

  def checkout_selected_books(self):
    """Check out selected books from the search results."""
    # Get currently selected books
    selected_isbns = self.get_selected_books()

    if not selected_isbns:
      messagebox.showwarning(
        "No Selection",
        "Please select at least one available book (highlighted in green).",
        parent=self.master,
      )
      return

    card_id = self.selected_card_id_entry.get().strip()
    if not card_id:
      messagebox.showerror(
        "Error", "Please enter a Borrower Card ID.", parent=self.master
      )
      return

    # Check out each selected book
    success_count = 0
    error_messages = []

    for isbn in selected_isbns:
      result = self.perform_checkout(isbn, card_id)
      if result["success"]:
        success_count += 1
      else:
        error_messages.append(f"ISBN {isbn}: {result['message']}")

    # Show results
    if success_count > 0:
      msg = f"Successfully checked out {success_count} book(s)."
      if error_messages:
        msg += "\n\nErrors:\n" + "\n".join(error_messages)
      messagebox.showinfo("Checkout Complete", msg, parent=self.master)

    if error_messages and success_count == 0:
      messagebox.showerror(
        "Checkout Failed", "\n".join(error_messages), parent=self.master
      )

    # Clear selections and refresh
    self.selected_card_id_entry.delete(0, tk.END)
    self.search_books_for_checkout()  # Refresh the list

  def perform_checkout(self, isbn: str, card_id: str) -> dict:
    """
    Wrapper for checkout function that returns result dict instead of printing.
    Returns: {'success': bool, 'message': str}
    """
    cursor = self.conn.cursor()

    # Check if ISBN exists
    cursor.execute("SELECT Isbn FROM BOOK WHERE Isbn = ?", (isbn,))
    if cursor.fetchone() is None:
      return {"success": False, "message": f"Book with ISBN {isbn} does not exist."}

    # Check if borrower exists
    cursor.execute("SELECT Card_id FROM BORROWER WHERE Card_id = ?", (card_id,))
    if cursor.fetchone() is None:
      return {
        "success": False,
        "message": f"Borrower with Card ID {card_id} does not exist.",
      }

    # Check if borrower has 3 active loans
    cursor.execute(
      """
            SELECT COUNT(*) FROM BOOK_LOANS
            WHERE Card_id = ? AND Date_in IS NULL
        """,
      (card_id,),
    )
    active_loans = cursor.fetchone()[0]

    if active_loans >= 3:
      return {
        "success": False,
        "message": f"Borrower {card_id} already has 3 active loans. Maximum of 3 active loans permitted per borrower.",
      }

    # Check if book is already checked out
    cursor.execute(
      """
            SELECT COUNT(*) FROM BOOK_LOANS
            WHERE Isbn = ? AND Date_in IS NULL
        """,
      (isbn,),
    )
    if cursor.fetchone()[0] > 0:
      return {
        "success": False,
        "message": f"Book with ISBN {isbn} is already checked out. The book is not available for checkout.",
      }

    # Check if borrower has unpaid fines
    cursor.execute(
      """
            SELECT COUNT(*) FROM FINES f
            JOIN BOOK_LOANS bl ON f.Loan_id = bl.Loan_id
            WHERE bl.Card_id = ? AND f.Paid = 0
        """,
      (card_id,),
    )
    unpaid_fines = cursor.fetchone()[0]

    if unpaid_fines > 0:
      return {
        "success": False,
        "message": f"Borrower {card_id} has unpaid fines. Cannot checkout books until all fines are paid.",
      }

    # All validations passed - proceed with checkout
    from datetime import date, timedelta

    today = date.today()
    due_date = today + timedelta(days=14)

    try:
      cursor.execute(
        """
                INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in)
                VALUES (?, ?, ?, ?, NULL)
            """,
        (isbn, card_id, today, due_date),
      )

      self.conn.commit()

      return {
        "success": True,
        "message": f"Book checked out successfully!\nISBN: {isbn}\nBorrower: {card_id}\nDate Out: {today}\nDue Date: {due_date}",
      }

    except sqlite3.Error as e:
      self.conn.rollback()
      return {"success": False, "message": f"Failed to checkout book: {e}"}

  def search_loans_for_checkin(self):
    """Search for loans and display in the table."""
    search_term = self.loan_search_entry.get().strip()

    if not search_term:
      messagebox.showwarning(
        "Input Required", "Please enter a search term.", parent=self.master
      )
      return

    # Clear old rows
    for row in self.loan_tree.get_children():
      self.loan_tree.delete(row)

    # Search loans using the function from book_loans.py
    # We need to get the data without printing, so let's query directly
    cursor = self.conn.cursor()
    pattern = f"%{search_term.lower().strip()}%"

    query = """
        SELECT
            bl.Loan_id,
            bl.Isbn,
            b.Title,
            bl.Card_id,
            br.First_name || ' ' || br.Last_name AS Borrower_name,
            bl.Date_out,
            bl.Due_date,
            bl.Date_in
        FROM BOOK_LOANS bl
        JOIN BOOK b ON bl.Isbn = b.Isbn
        JOIN BORROWER br ON bl.Card_id = br.Card_id
        WHERE
            CAST(bl.Isbn AS TEXT) LIKE ?
            OR bl.Card_id LIKE ?
            OR LOWER(br.First_name) LIKE ?
            OR LOWER(br.Last_name) LIKE ?
            OR LOWER(br.First_name || ' ' || br.Last_name) LIKE ?
        ORDER BY bl.Date_out DESC, bl.Due_date
    """

    cursor.execute(query, (pattern, pattern, pattern, pattern, pattern))
    self.loan_data = cursor.fetchall()

    if not self.loan_data:
      messagebox.showinfo(
        "No Results", f"No loans found matching '{search_term}'.", parent=self.master
      )
      self.checkin_result_label.config(text="No loans found")
      return

    # Insert results into tree
    for (
      loan_id,
      isbn,
      title,
      card_id,
      borrower_name,
      date_out,
      due_date,
      date_in,
    ) in self.loan_data:
      status = "OUT" if date_in is None else "IN"
      # Truncate long titles
      title_display = title[:50] + "..." if len(title) > 50 else title

      self.loan_tree.insert(
        "",
        tk.END,
        values=(
          loan_id,
          isbn,
          title_display,
          card_id,
          borrower_name,
          str(date_out),
          str(due_date),
          status,
        ),
        tags=("out" if status == "OUT" else "in",),
      )

    # Configure tags
    self.loan_tree.tag_configure("out", background="lightyellow")
    self.loan_tree.tag_configure("in", background="lightgray")

    # Update result count
    self.checkin_result_label.config(text=f"Found {len(self.loan_data)} loan(s)")

  def checkin_selected_loans(self):
    """Check in selected loans."""
    selection = self.loan_tree.selection()

    if not selection:
      messagebox.showwarning(
        "No Selection",
        "Please select at least one loan to check in.",
        parent=self.master,
      )
      return

    # Get loan IDs from selection
    loan_ids = []
    for item_id in selection:
      item = self.loan_tree.item(item_id)
      loan_id = item["values"][0]
      status = item["values"][7]

      if status == "IN":
        messagebox.showwarning(
          "Already Checked In",
          f"Loan ID {loan_id} is already checked in.",
          parent=self.master,
        )
        continue

      loan_ids.append(loan_id)

    if not loan_ids:
      messagebox.showwarning(
        "No Valid Selection",
        "No valid loans selected for check-in.",
        parent=self.master,
      )
      return

    if len(loan_ids) > 3:
      messagebox.showerror(
        "Too Many Loans",
        "Cannot check in more than 3 loans at once.",
        parent=self.master,
      )
      return

    # Confirm
    confirm = messagebox.askyesno(
      "Confirm Check-In",
      f"Check in {len(loan_ids)} loan(s)?\nLoan IDs: {', '.join(map(str, loan_ids))}",
      parent=self.master,
    )

    if not confirm:
      return

    # Perform check-in using the function from book_loans.py
    result = checkin(loan_ids, self.conn)

    if result:
      messagebox.showinfo(
        "Success",
        f"Successfully checked in {len(loan_ids)} loan(s).",
        parent=self.master,
      )
      # Refresh the search
      self.search_loans_for_checkin()
    else:
      messagebox.showerror(
        "Error", "Failed to check in one or more loans.", parent=self.master
      )

    ttk.Label(self.master, text="Pranav Thoppe, your code will go here").pack()


def start_book_loans_gui(conn):
  """Launch the Book Loans GUI."""
  root = tk.Tk()
  app = BookLoansGUI(root, conn)
  root.mainloop()
