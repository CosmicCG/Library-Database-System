import tkinter as tk
from decimal import Decimal
from tkinter import messagebox, ttk

from fines import pay_fines, update_all_fines


class FinesGUI:
  def __init__(self, root, conn):
    self.root = root
    self.conn = conn
    self.root.title("Fines Management")
    self.root.geometry("800x600")

    search_frame = tk.Frame(root)
    search_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(search_frame, text="Borrower ID:").grid(row=0, column=0)
    self.borrower_id_entry = tk.Entry(search_frame, width=12)
    self.borrower_id_entry.grid(row=0, column=1, padx=5)

    tk.Label(search_frame, text="Name Contains:").grid(row=0, column=2)
    self.name_entry = tk.Entry(search_frame, width=20)
    self.name_entry.grid(row=0, column=3, padx=5)

    self.include_paid_var = tk.IntVar()
    tk.Checkbutton(
      search_frame, text="Include Paid Fines", variable=self.include_paid_var
    ).grid(row=0, column=4, padx=5)

    tk.Button(search_frame, text="Search", command=self.search_fines).grid(
      row=0, column=5, padx=10
    )

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(fill="x", padx=10, pady=5)

    tk.Button(btn_frame, text="Refresh Fines", command=self.update_fines).pack(
      side="left", padx=10
    )
    tk.Button(btn_frame, text="Pay Selected Fines", command=self.pay_selected).pack(
      side="left", padx=10
    )

    # Table
    table_frame = tk.Frame(root)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("card_no", "name", "total_fines", "paid")
    self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    self.tree.heading("card_no", text="Borrower ID")
    self.tree.heading("name", text="Borrower Name")
    self.tree.heading("total_fines", text="Total Fines ($)")
    self.tree.heading("paid", text="Paid?")

    self.tree.column("card_no", width=120)
    self.tree.column("name", width=250)
    self.tree.column("total_fines", width=120)
    self.tree.column("paid", width=80)

    self.tree.pack(fill="both", expand=True)

    # Button Logic

  def update_fines(self):
    update_all_fines(self.conn)
    messagebox.showinfo(
      "Fines Updated", "All fines have been refreshed.", parent=self.root
    )
    self.search_fines()

  def search_fines(self):
    borrower_id = self.borrower_id_entry.get().strip()
    name_substring = self.name_entry.get().strip()
    include_paid = bool(self.include_paid_var.get())

    cursor = self.conn.cursor()
    self.conn.row_factory = None  # Default for SQL execution

    # Build SQL query based on filters
    sql = """
            SELECT
                B.Card_id AS card_no,
                CONCAT(BR.First_name, ' ', BR.Last_name) AS Name,
                SUM(F.Fine_amt) AS Total_Fines,
                CASE
                    WHEN MIN(F.Paid) = 1 AND MAX(F.Paid) = 1 THEN 1
                    ELSE 0
                END AS paid
            FROM FINES F
            JOIN BOOK_LOANS B ON F.Loan_id = B.Loan_id
            JOIN BORROWER BR ON B.Card_id = BR.Card_id
        """

    where_clauses = []
    params = []

    if not include_paid:
      where_clauses.append("F.Paid = 0")

    if borrower_id:
      where_clauses.append("BR.Card_ID = ?")
      params.append(borrower_id)

    if name_substring:
      where_clauses.append("Name LIKE ?")
      params.append(f"%{name_substring}%")

    if where_clauses:
      sql += " WHERE " + " AND ".join(where_clauses)

    sql += " GROUP BY B.Card_id ORDER BY Name"

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    # Clear table
    for item in self.tree.get_children():
      self.tree.delete(item)

    # Insert results
    for row in rows:
      card_no = row[0]
      name = row[1]
      total_fines = Decimal(str(row[2])).quantize(Decimal("0.00"))
      paid = "Yes" if row[3] else "No"

      self.tree.insert("", tk.END, values=(card_no, name, total_fines, paid))

  def pay_selected(self):
    selected = self.tree.selection()
    if not selected:
      messagebox.showwarning(
        "No Selection", "Please select a borrower.", parent=self.root
      )
      return

    borrower_id = self.tree.item(selected[0])["values"][0]

    success = pay_fines(self.conn, borrower_id)
    if success:
      messagebox.showinfo(
        "Payment Successful", "All outstanding fines have been paid.", parent=self.root
      )
      self.search_fines()


def start_fines_gui(conn):
  root = tk.Tk()
  FinesGUI(root, conn)
  root.mainloop()
