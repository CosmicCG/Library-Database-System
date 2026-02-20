import re
import sqlite3


def get_next_card_id(conn: sqlite3.Connection) -> str:
  """Generate the next Card_id for a new borrower."""
  cur = conn.cursor()
  cur.execute("SELECT MAX(Card_id) FROM BORROWER;")
  result = cur.fetchone()[0]
  if result is None:
    return "ID000001"
  match = re.match(r"ID(\d+)", result)
  if match:
    current_num = int(match.group(1))
    next_id_num = current_num + 1
    return f"ID{next_id_num:06d}"
  else:
    return "ID000001"


def check_ssn_exists(ssn: str, conn: sqlite3.Connection) -> bool:
  """Check if a borrower with the given SSN already exists."""
  cur = conn.cursor()
  cur.execute("SELECT COUNT(*) FROM BORROWER WHERE SSN = ?", (ssn,))
  count = cur.fetchone()[0]
  return count > 0


def validate_phone(phone: str) -> bool:
  """Validate phone number format (simple check for digits and length)."""
  cleaned = re.sub(r"[\s\-\(\)]", "", phone)
  return len(cleaned) == 10 and cleaned.isdigit()


def create_borrower(conn: sqlite3.Connection) -> bool:
  """Create a new borrower in the database."""
  print("\n")
  print("Create New Borrower")
  print("\n")
  print("\nPlease enter the following information:")
  print("(All fields marked with * are required)\n")

  # SSN - Required
  while True:
    ssn = input("* SSN (format: XXX-XX-XXXX): ").strip()
    if not ssn:
      print("  ERROR: SSN is required!")
      continue
    # Basic SSN format validation
    if not re.match(r"^\d{3}-\d{2}-\d{4}$", ssn):
      print("  ERROR: Invalid SSN format. Use XXX-XX-XXXX")
      continue
    if check_ssn_exists(ssn, conn):
      print("  ERROR: A borrower with this SSN already exists!")
      print("  Borrowers are allowed to possess exactly one library card.")
      return False
    break

  # First Name - Required
  while True:
    first_name = input("* First Name: ").strip()
    if not first_name:
      print("  ERROR: First name is required!")
      continue
    break

  # Last Name - Required
  while True:
    last_name = input("* Last Name: ").strip()
    if not last_name:
      print("  ERROR: Last name is required!")
      continue
    break

  # Address - Required
  while True:
    address = input("* Address: ").strip()
    if not address:
      print("  ERROR: Address is required!")
      continue
    break

  # Optional fields
  email = input("  Email (optional): ").strip() or None
  city = input("  City (optional): ").strip() or None
  state = input("  State (optional): ").strip() or None

  # Phone - Optional but validate if provided
  phone = None
  while True:
    phone_input = input("  Phone (optional, format: (XXX) XXX-XXXX): ").strip()
    if not phone_input:
      phone = None
      break
    if validate_phone(phone_input):
      phone = phone_input
      break
    else:
      print("  WARNING: Invalid phone format. Please use (XXX) XXX-XXXX")
      retry = input("  Try again? (y/n): ").strip().lower()
      if retry != "y":
        phone = None
        break

  # Generate new Card_id
  card_id = get_next_card_id(conn)

  # Confirm before creating
  print("\nCONFIRM NEW BORROWER INFORMATION:\n")
  print(f"Card ID:    {card_id}")
  print(f"Name:       {first_name} {last_name}")
  print(f"SSN:        {ssn}")
  print(f"Address:    {address}")
  if city:
    print(f"City:       {city}")
  if state:
    print(f"State:      {state}")
  if email:
    print(f"Email:      {email}")
  if phone:
    print(f"Phone:      {phone}")
  print("-" * 60)

  confirm = input("\nCreate this borrower? (y/n): ").strip().lower()

  if confirm != "y":
    print("\nBorrower creation cancelled.")
    return False

  # Insert into database
  try:
    cursor = conn.cursor()
    cursor.execute(
      """
            INSERT INTO BORROWER (Card_id, SSN, First_name, Last_name, Email, Address, City, State, Phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
      (card_id, ssn, first_name, last_name, email, address, city, state, phone),
    )

    conn.commit()

    print("\n")
    print("✓ SUCCESS: Borrower created successfully!")
    print(f"✓ New Card ID: {card_id}")
    print("\n")

    return True

  except sqlite3.Error as e:
    print(f"\n✗ ERROR: Failed to create borrower: {e}\n")
    conn.rollback()
    return False


def search_borrower(conn: sqlite3.Connection):
  """Search for borrowers by name or SSN."""
  print("\n")
  print("Search Borrowers")
  print("\n")

  search_term = input("\nSearch (Name/Card ID/SSN): ").strip()
  if not search_term:
    print("  No search term provided.")
    return

  cursor = conn.cursor()
  query = """
        SELECT Card_id, SSN, First_name, Last_name, Email, Address, City, State, Phone
        FROM BORROWER
        WHERE LOWER(First_name) LIKE ?
           OR LOWER(Last_name) LIKE ?
           OR Card_id LIKE ?
           OR SSN LIKE ?
        ORDER BY Last_name, First_name;
    """
  pattern = f"%{search_term.lower()}%"
  cursor.execute(query, (pattern, pattern, pattern, pattern))
  results = cursor.fetchall()

  if not results:
    print(f"\nNo borrowers found matching '{search_term}'.\n")
    return

  print(f"\nFound {len(results)} borrower(s):\n")
  print(
    f"{'Card ID':<12} {'Name':<30} {'SSN':<15} {'Email':<30} {'Address':<35} {'Phone':<18} {'Location':<20}"
  )
  print("-" * 160)

  for card_id, ssn, first, last, email, address, city, state, phone in results:
    name = f"{first} {last}"
    email_display = email or "N/A"
    address_display = address or "N/A"
    phone_display = phone or "N/A"
    location = f"{city}, {state}" if city and state else (city or state or "N/A")
    print(
      f"{card_id:<12} {name:<30} {ssn:<15} {email_display:<30} {address_display:<35} {phone_display:<18} {location:<20}"
    )
  print()


def borrower_management_menu(conn: sqlite3.Connection):
  """Borrower Management Submenu."""

  while True:
    print("\nBorrower Management Menu\n")
    print("1) Create New Borrower")
    print("2) Search Borrowers")
    print("0) Return to Main Menu\n")

    choice = input("Enter your choice: ").strip()

    match choice:
      case "1":
        create_borrower(conn)
      case "2":
        search_borrower(conn)
      case "0":
        print("Returning to Main Menu...")
        break
      case _:
        print("Invalid choice. Please try again.")
