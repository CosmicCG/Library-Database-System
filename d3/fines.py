import sqlite3
from datetime import date
from decimal import Decimal

# from tkinter.constants import W

DAILY_FINE = Decimal("0.25")

# class FineManager:
#  def __init__(self, conn):
#    self.cursor = conn.cursor()
#    self.db = mysql.connector.connect(**db_config)
#    self.cursor = self.db.cursor(dictionary=True)


# Terminal menu manager for managing fines
def Fines_Menu(conn: sqlite3.Connection):
  # Code for the fine manager menu will go here
  while True:
    # Menu Options
    print("\n\nFines Menu Options:")
    print("1. Update all fines")
    print("2. Get fines grouped by borrower")
    print("3. Pay Fines")
    print("0. Exit")

    # Get user input
    userInput = int(input("Enter your menu choice: "))
    match userInput:
      case 0:
        print("Returning to main menu...")
        break
      case 1:
        update_all_fines(conn)
      case 2:
        update_all_fines(conn)
        # Get results based on inlcuding paid values or not
        paid = input("Do you want to include paid fines? (y/N): ")
        if paid == "y":
          results = get_fines_by_borrower(conn, True)
        else:
          results = get_fines_by_borrower(conn)
        # Display results
        for result in results:
          print(dict(result))
      case 3:
        card_no = input("Enter card number: ")
        update_all_fines(conn)
        pay_fines(conn, card_no)
      case _:
        print("Invalid choice")


# Calculate fines for a loan
def calculate_fine(due_date, date_in):
  today = date.today()

  if date_in is not None:
    late_days = (date_in - due_date).days
  else:
    late_days = (today - due_date).days

  if late_days <= 0:
    return Decimal("0.00")

  return DAILY_FINE * late_days


# Cron function to refresh ALL FINES table entries
def update_all_fines(conn: sqlite3.Connection):
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM BOOK_LOANS")
  loans = cursor.fetchall()

  for loan in loans:
    fine_amt = calculate_fine(loan["Due_date"], loan["Date_in"])
    update_fine_entry(conn, loan["Loan_id"], fine_amt)

  conn.commit()


# Update or create fine entry for a single loan
def update_fine_entry(conn: sqlite3.Connection, loan_id, fine_amt):
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM FINES WHERE Loan_id = ?", (loan_id,))
  existing = cursor.fetchone()

  # No fine and not late
  if fine_amt == 0 and existing is None:
    return

  # Existing unpaid fine
  if existing and not existing["Paid"]:
    if existing["Fine_amt"] != fine_amt:
      cursor.execute(
        "UPDATE FINES SET Fine_amt = ? WHERE Loan_id = ?",
        (fine_amt, existing["Loan_id"]),
      )
    return

  # Existing paid fine
  if existing and existing["Paid"]:
    return

  # Create a new fine
  cursor.execute(
    "INSERT INTO FINES (Loan_id, Fine_amt, Paid) VALUES (?, ?, 0)",
    (loan_id, fine_amt),
  )


# Get grouped fines by borrower
def get_fines_by_borrower(conn: sqlite3.Connection, include_paid=False):
  query = """
          SELECT B.Card_id, SUM(F.Fine_amt) AS Total_Fines
          FROM FINES F
          JOIN BOOK_LOANS B ON F.Loan_id = B.Loan_id
      """
  if not include_paid:
    query += " WHERE F.Paid = 0"
  query += " GROUP BY B.Card_id"

  cursor = conn.cursor()
  cursor.execute(query)
  results = cursor.fetchall()
  return results


# Pay all fines for a card_no
def pay_fines(conn: sqlite3.Connection, card_no):
  cursor = conn.cursor()
  # Cannot pay for books not returned
  query = """
    SELECT F.Loan_id, B.Date_in
    FROM FINES F
    JOIN BOOK_LOANS B ON F.Loan_id = B.Loan_id
    WHERE B.Card_id = ? AND F.Paid = 0
  """
  cursor.execute(query, (card_no,))
  fines = cursor.fetchall()

  if not fines:
    print("No outstanding fines.")
    return False

  # Check if any book is still out
  for fine in fines:
    if fine["Date_in"] is None:
      print("Unable to pay fines: a book has not been returned.")
      return False

  # Pay all fines (partial payment disallowed)
  cursor.execute(
    """
          UPDATE FINES
          SET Paid = 1
          FROM FINES F
          JOIN BOOK_LOANS B ON F.Loan_id = B.Loan_id
          WHERE B.Card_id = ?
      """,
    (card_no,),
  )
  conn.commit()

  print("Payment successful. All fines cleared.")
  return True
