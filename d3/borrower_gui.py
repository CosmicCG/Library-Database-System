import re
import tkinter as tk
from tkinter import messagebox, ttk

# Import functions to use from borrower_management.py
from borrower_management import check_ssn_exists, get_next_card_id, validate_phone


class BorrowerGUI:
  def __init__(self, root, conn):
    self.root = root
    self.root.title("Library Borrower Management")
    self.conn = conn

    # Create notebook for tabs
    self.notebook = ttk.Notebook(root)
    self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Create two tabs
    self.create_tab = tk.Frame(self.notebook)
    self.search_tab = tk.Frame(self.notebook)

    self.notebook.add(self.create_tab, text="Create Borrower")
    self.notebook.add(self.search_tab, text="Search Borrowers")

    # Set up both tabs
    self.setup_create_tab()
    self.setup_search_tab()

  # Sets up the "Create Borrower" tab
  def setup_create_tab(self):
    # Title
    tk.Label(
      self.create_tab, text="Create New Borrower", font=("Arial", 14, "bold")
    ).pack(pady=10)
    tk.Label(self.create_tab, text="* = required field", font=("Arial", 9)).pack()

    # Form frame
    form_frame = tk.Frame(self.create_tab)
    form_frame.pack(pady=20)

    # Dictionary to store entry widgets
    self.entries = {}
    row = 0

    # SSN field
    tk.Label(form_frame, text="* SSN (XXX-XX-XXXX):").grid(
      row=row, column=0, sticky="e", padx=5, pady=5
    )
    self.entries["ssn"] = ttk.Entry(form_frame, width=30)
    self.entries["ssn"].grid(row=row, column=1, padx=5, pady=5)
    row += 1

    # First Name field
    tk.Label(form_frame, text="* First Name:").grid(
      row=row, column=0, sticky="e", padx=5, pady=5
    )
    self.entries["first_name"] = ttk.Entry(form_frame, width=30)
    self.entries["first_name"].grid(row=row, column=1, padx=5, pady=5)
    row += 1

    # Last Name field
    tk.Label(form_frame, text="* Last Name:").grid(
      row=row, column=0, sticky="e", padx=5, pady=5
    )
    self.entries["last_name"] = ttk.Entry(form_frame, width=30)
    self.entries["last_name"].grid(row=row, column=1, padx=5, pady=5)
    row += 1

    # Address field
    tk.Label(form_frame, text="* Address:").grid(
      row=row, column=0, sticky="e", padx=5, pady=5
    )
    self.entries["address"] = ttk.Entry(form_frame, width=30)
    self.entries["address"].grid(row=row, column=1, padx=5, pady=5)
    row += 1

    # Separator
    tk.Label(form_frame, text="Optional Fields:", font=("Arial", 9, "italic")).grid(
      row=row, column=0, columnspan=2, pady=10
    )
    row += 1

    # Email field
    tk.Label(form_frame, text="Email:").grid(
      row=row, column=0, sticky="e", padx=5, pady=5
    )
    self.entries["email"] = ttk.Entry(form_frame, width=30)
    self.entries["email"].grid(row=row, column=1, padx=5, pady=5)
    row += 1

    # City field
    tk.Label(form_frame, text="City:").grid(
      row=row, column=0, sticky="e", padx=5, pady=5
    )
    self.entries["city"] = ttk.Entry(form_frame, width=30)
    self.entries["city"].grid(row=row, column=1, padx=5, pady=5)
    row += 1

    # State field
    tk.Label(form_frame, text="State:").grid(
      row=row, column=0, sticky="e", padx=5, pady=5
    )
    self.entries["state"] = ttk.Entry(form_frame, width=30)
    self.entries["state"].grid(row=row, column=1, padx=5, pady=5)
    row += 1

    # Phone field
    tk.Label(form_frame, text="Phone:").grid(
      row=row, column=0, sticky="e", padx=5, pady=5
    )
    self.entries["phone"] = ttk.Entry(form_frame, width=30)
    self.entries["phone"].grid(row=row, column=1, padx=5, pady=5)

    # Buttons
    button_frame = tk.Frame(self.create_tab)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Create Borrower", command=self.perform_create).pack(
      side=tk.LEFT, padx=5
    )
    ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(
      side=tk.LEFT, padx=5
    )

  # Sets up the "Search Borrowers" tab
  def setup_search_tab(self):
    # Search bar frame
    search_frame = tk.Frame(self.search_tab)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Search Borrowers: ").pack(side=tk.LEFT)

    # User types search keyword here
    self.search_entry = ttk.Entry(search_frame, width=50)
    self.search_entry.bind("<Return>", self.perform_search_event)
    self.search_entry.pack(side=tk.LEFT, padx=5)

    # Button to actually run search
    ttk.Button(search_frame, text="Search", command=self.perform_search).pack(
      side=tk.LEFT
    )

    # Set up results table
    columns = ("Card_ID", "Name", "SSN", "Email", "Address", "City", "State", "Phone")
    self.tree = ttk.Treeview(
      self.search_tab, columns=columns, show="headings", height=12
    )

    # Set headings
    for col in columns:
      self.tree.heading(col, text=col)
      # wider columns for name and address
      if col == "Name":
        self.tree.column(col, width=180)
      elif col == "Address":
        self.tree.column(col, width=200)
      elif col == "Email":
        self.tree.column(col, width=180)
      else:
        self.tree.column(col, width=100)

    self.tree.pack(pady=10)

    # Label to show result count
    self.result_label = tk.Label(self.search_tab, text="")
    self.result_label.pack()

  # Validates SSN format using same regex as borrower_management.py
  def validate_ssn(self, ssn):
    return bool(re.match(r"^\d{3}-\d{2}-\d{4}$", ssn))

  # Runs whenever the user clicks "Create Borrower"
  def perform_create(self):
    # Get all values
    ssn = self.entries["ssn"].get().strip()
    first_name = self.entries["first_name"].get().strip()
    last_name = self.entries["last_name"].get().strip()
    address = self.entries["address"].get().strip()
    email = self.entries["email"].get().strip() or None
    city = self.entries["city"].get().strip() or None
    state = self.entries["state"].get().strip() or None
    phone = self.entries["phone"].get().strip() or None

    # Validate required fields
    if not ssn:
      messagebox.showerror("Error", "SSN is required!", parent=self.root)
      return

    if not self.validate_ssn(ssn):
      messagebox.showerror(
        "Error", "Invalid SSN format. Use XXX-XX-XXXX", parent=self.root
      )
      return

    if check_ssn_exists(ssn, self.conn):
      messagebox.showerror(
        "Error",
        "A borrower with this SSN already exists!\n"
        + "Borrowers are allowed exactly one library card.",
        parent=self.root,
      )
      return

    if not first_name:
      messagebox.showerror("Error", "First name is required!", parent=self.root)
      return

    if not last_name:
      messagebox.showerror("Error", "Last name is required!", parent=self.root)
      return

    if not address:
      messagebox.showerror("Error", "Address is required!", parent=self.root)
      return

    if phone and not validate_phone(phone):
      messagebox.showwarning(
        "Warning",
        "Invalid phone format. Phone will be saved as-is.\n"
        + "Standard format is (XXX) XXX-XXXX",
        parent=self.root,
      )

    card_id = get_next_card_id(self.conn)

    # Ask user to confirm
    confirm_msg = f"Create new borrower?\n\nCard ID: {card_id}\nName: {first_name} {last_name}\nSSN: {ssn}"

    if not messagebox.askyesno("Confirm", confirm_msg, parent=self.root):
      return

    # Insert into database
    try:
      cursor = self.conn.cursor()
      cursor.execute(
        """
                INSERT INTO BORROWER (Card_id, SSN, First_name, Last_name, Email, Address, City, State, Phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
        (card_id, ssn, first_name, last_name, email, address, city, state, phone),
      )

      self.conn.commit()

      messagebox.showinfo(
        "Success",
        f"Borrower created successfully!\nNew Card ID: {card_id}",
        parent=self.root,
      )
      self.clear_form()

    except Exception as e:
      messagebox.showerror(
        "Database Error", f"Failed to create borrower:\n{e}", parent=self.root
      )
      self.conn.rollback()

  # Clears all form fields
  def clear_form(self):
    for entry in self.entries.values():
      entry.delete(0, tk.END)

  def perform_search_event(self, event):
    self.perform_search()

  # Runs whenever the user clicks "Search"
  def perform_search(self):
    keyword = self.search_entry.get().strip()

    # Clear old rows from the table
    for row in self.tree.get_children():
      self.tree.delete(row)

    if keyword == "":
      messagebox.showwarning(
        "Input Required", "Please enter a search term.", parent=self.root
      )
      return

    # Query the database
    cursor = self.conn.cursor()
    query = """
            SELECT Card_id, SSN, First_name, Last_name, Email, Address, City, State, Phone
            FROM BORROWER
            WHERE LOWER(First_name) LIKE ?
               OR LOWER(Last_name) LIKE ?
               OR LOWER(First_name || ' ' || Last_name) LIKE ?
               OR Card_id LIKE ?
               OR SSN LIKE ?
            ORDER BY Last_name, First_name
        """

    pattern = f"%{keyword.lower()}%"
    cursor.execute(query, (pattern, pattern, pattern, pattern, pattern))
    results = cursor.fetchall()

    if not results:
      messagebox.showinfo(
        "No Results", f"No borrowers found matching '{keyword}'.", parent=self.root
      )
      self.result_label.config(text="")
      return

    # Insert each row into the table
    for card_id, ssn, first, last, email, address, city, state, phone in results:
      name = f"{first} {last}"
      self.tree.insert(
        "",
        tk.END,
        values=(
          card_id,
          name,
          ssn,
          email or "N/A",
          address or "N/A",
          city or "N/A",
          state or "N/A",
          phone or "N/A",
        ),
      )

    self.result_label.config(text=f"Found {len(results)} borrower(s)")


# Launches the GUI when called
def start_borrower_gui(conn):
  root = tk.Tk()
  BorrowerGUI(root, conn)
  root.mainloop()
