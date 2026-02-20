import sqlite3
from datetime import date, timedelta


def checkout(isbn: str, card_id: str, conn: sqlite3.Connection) -> bool:
  """
  Check out a book for a borrower.

  Validations:
  - Borrower must not have 3 active loans
  - Book must be available (not currently checked out)
  - Borrower must not have unpaid fines

  Returns True if successful, False otherwise.
  """
  cursor = conn.cursor()

  # Check if ISBN exists
  cursor.execute("SELECT Isbn FROM BOOK WHERE Isbn = ?", (isbn,))
  if cursor.fetchone() is None:
    print(f"\n✗ ERROR: Book with ISBN {isbn} does not exist.\n")
    return False

  # Check if borrower exists
  cursor.execute("SELECT Card_id FROM BORROWER WHERE Card_id = ?", (card_id,))
  if cursor.fetchone() is None:
    print(f"\n✗ ERROR: Borrower with Card ID {card_id} does not exist.\n")
    return False

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
    print(f"\n✗ ERROR: Borrower {card_id} already has 3 active loans.")
    print("\nMaximum of 3 active loans permitted per borrower.\n")
    return False

  # Check if book is already checked out
  cursor.execute(
    """
        SELECT COUNT(*) FROM BOOK_LOANS
        WHERE Isbn = ? AND Date_in IS NULL
    """,
    (isbn,),
  )
  if cursor.fetchone()[0] > 0:
    print(f"\n✗ ERROR: Book with ISBN {isbn} is already checked out.")
    print("  The book is not available for checkout.\n")
    return False

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
    print(f"\n✗ ERROR: Borrower {card_id} has unpaid fines.")
    print("  Cannot checkout books until all fines are paid.\n")
    return False

  # All validations passed - proceed with checkout
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

    conn.commit()

    print("\n✓ SUCCESS: Book checked out successfully!")
    print(f"  ISBN: {isbn}")
    print(f"  Borrower: {card_id}")
    print(f"  Date Out: {today}")
    print(f"  Due Date: {due_date}")
    print()

    return True

  except sqlite3.Error as e:
    print(f"\n✗ ERROR: Failed to checkout book: {e}\n")
    conn.rollback()
    return False


def search_loans(search_term: str, conn: sqlite3.Connection):
  """
  Search for book loans by ISBN, card_no, or borrower name.
  Returns list of loan tuples.
  """
  cursor = conn.cursor()

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
  results = cursor.fetchall()

  if not results:
    print(f"\nNo loans found matching '{search_term}'.\n")
    return []

  print(f"\nFound {len(results)} loan(s):\n")
  print(
    f"{'#':<4} {'Loan ID':<8} {'ISBN':<15} {'Title':<50} {'Card ID':<12} {'Borrower':<25} {'Date Out':<12} {'Due Date':<12} {'Status':<8}"
  )
  print("-" * 150)

  for idx, (
    loan_id,
    isbn,
    title,
    card_id,
    borrower_name,
    date_out,
    due_date,
    date_in,
  ) in enumerate(results, 1):
    status = "OUT" if date_in is None else "IN"
    title_display = title[:47] + "..." if len(title) > 50 else title
    borrower_display = (
      borrower_name[:23] + "..." if len(borrower_name) > 25 else borrower_name
    )

    print(
      f"{idx:<4} {loan_id:<8} {isbn:<15} {title_display:<50} {card_id:<12} {borrower_display:<25} {str(date_out):<12} {str(due_date):<12} {status:<8}"
    )

  print()
  return results


def checkin(loan_ids: list, conn: sqlite3.Connection) -> bool:
  """
  Check in 1-3 book loans.

  Args:
      loan_ids: List of loan IDs to check in (1-3 loans)
      conn: Database connection

  Returns True if all successful, False otherwise.
  """
  if not loan_ids or len(loan_ids) == 0:
    print("\n✗ ERROR: No loans selected for check-in.\n")
    return False

  if len(loan_ids) > 3:
    print("\n✗ ERROR: Cannot check in more than 3 loans at once.\n")
    return False

  cursor = conn.cursor()
  today = date.today()
  successful = 0
  failed = 0

  for loan_id in loan_ids:
    try:
      # Check if loan exists and is not already checked in
      cursor.execute(
        """
                SELECT Loan_id, Isbn, Card_id, Date_in
                FROM BOOK_LOANS
                WHERE Loan_id = ?
            """,
        (loan_id,),
      )

      loan = cursor.fetchone()
      if loan is None:
        print(f"✗ ERROR: Loan ID {loan_id} does not exist.")
        failed += 1
        continue

      if loan[3] is not None:  # Date_in is not NULL
        print(f"✗ ERROR: Loan ID {loan_id} is already checked in.")
        failed += 1
        continue

      # Check in the loan
      cursor.execute(
        """
                UPDATE BOOK_LOANS
                SET Date_in = ?
                WHERE Loan_id = ?
            """,
        (today, loan_id),
      )

      successful += 1
      print(f"✓ Loan ID {loan_id} checked in successfully (Date: {today})")

    except sqlite3.Error as e:
      print(f"✗ ERROR: Failed to check in Loan ID {loan_id}: {e}")
      failed += 1

  if successful > 0:
    conn.commit()
    print(f"\n✓ SUCCESS: {successful} loan(s) checked in successfully.\n")

  if failed > 0:
    conn.rollback()
    print(f"✗ {failed} loan(s) failed to check in.\n")
    return False

  return True


def checkout_interactive(conn: sqlite3.Connection):
  """Interactive function to checkout a book."""
  print("\nCheck Out Book\n")

  isbn = input("Enter ISBN: ").strip()
  if not isbn:
    print("  ERROR: ISBN is required.\n")
    return

  card_id = input("Enter Borrower Card ID: ").strip()
  if not card_id:
    print("  ERROR: Borrower Card ID is required.\n")
    return

  checkout(isbn, card_id, conn)


def checkin_interactive(conn: sqlite3.Connection):
  """Interactive function to check in books."""
  print("\nCheck In Books\n")

  search_term = input("Search loans by ISBN, Card ID, or Borrower Name: ").strip()
  if not search_term:
    print("  ERROR: Search term is required.\n")
    return

  # Search for loans
  loans = search_loans(search_term, conn)

  if not loans:
    return

  # Get loan IDs to check in
  print(
    "Enter the loan numbers (#) to check in (1-3 loans, separated by commas, i.e. 2,4,6):"
  )
  selection = input("Selection: ").strip()

  if not selection:
    print("  No selection made.\n")
    return

  try:
    # Parse selection (e.g., "1,2,3" or "1")
    indices = [int(x.strip()) - 1 for x in selection.split(",")]

    if len(indices) > 3:
      print("\n✗ ERROR: Cannot select more than 3 loans.\n")
      return

    if any(idx < 0 or idx >= len(loans) for idx in indices):
      print("\n✗ ERROR: Invalid loan number(s) selected.\n")
      return

    # Get loan IDs from the selected indices
    loan_ids = [loans[idx][0] for idx in indices]  # loans[idx][0] is Loan_id

    # Confirm
    print(f"\nSelected {len(loan_ids)} loan(s) to check in.")
    confirm = input("Confirm check-in? (y/n): ").strip().lower()

    if confirm != "y":
      print("Check-in cancelled.\n")
      return

    checkin(loan_ids, conn)

  except ValueError:
    print(
      "\n✗ ERROR: Invalid input. Please enter numbers separated by commas (e.g., 1,2,3).\n"
    )


def book_loans_menu(conn: sqlite3.Connection):
  """Book Loans Submenu."""
  while True:
    print("\nBook Loans Menu\n")
    print("1) Check Out Book")
    print("2) Check In Books")
    print("0) Return to Main Menu\n")

    choice = input("Enter your choice: ").strip()

    match choice:
      case "1":
        checkout_interactive(conn)
      case "2":
        checkin_interactive(conn)
      case "0":
        print("Returning to Main Menu...")
        break
      case _:
        print("Invalid choice. Please try again.")
