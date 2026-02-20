import sqlite3

import pandas as pd

# Connecting python to SQLite

conn = sqlite3.connect("library.db")
cur = conn.cursor()

# Dropping and Recreating tables

tables = ["BOOK", "BOOK_AUTHORS", "AUTHORS", "BORROWER", "BOOK_LOANS", "FINES"]
for t in tables:
  cur.execute(f"DROP TABLE IF EXISTS {t};")

cur.executescript("""
CREATE TABLE BOOK (
    Isbn INTEGER PRIMARY KEY,
    Title TEXT NOT NULL
);

CREATE TABLE AUTHORS (
    Author_id INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);

CREATE TABLE BOOK_AUTHORS (
    Isbn INTEGER,
    Author_id INTEGER,
    FOREIGN KEY (Isbn) REFERENCES BOOK(Isbn),
    FOREIGN KEY (Author_id) REFERENCES AUTHORS(Author_id)
);

CREATE TABLE BORROWER (
    Card_id TEXT PRIMARY KEY,
    SSN TEXT NOT NULL,
    First_name TEXT NOT NULL,
    Last_name TEXT NOT NULL,
    Email TEXT,
    Address TEXT,
    City TEXT,
    State TEXT,
    Phone TEXT
);

CREATE TABLE BOOK_LOANS (
    Loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    Isbn INTEGER,
    Card_id TEXT,
    Date_out DATE,
    Due_date DATE,
    Date_in DATE,
    FOREIGN KEY (Isbn) REFERENCES BOOK(Isbn),
    FOREIGN KEY (Card_id) REFERENCES BORROWER(Card_id)
);

CREATE TABLE FINES (
    Loan_id INTEGER,
    Fine_amt DECTEXT,
    Paid INTEGER DEFAULT 0,
    FOREIGN KEY (Loan_id) REFERENCES BOOK_LOANS(Loan_id)
);
""")

# Loading the CSVs
book = pd.read_csv("book.csv", keep_default_na=False)
book_authors = pd.read_csv("book_authors.csv", keep_default_na=False)
authors = pd.read_csv("authors.csv", keep_default_na=False)
borrower = pd.read_csv("borrower.csv", keep_default_na=False)


#  Cleaning book csv
# Normalizing ISBN digits
book["Isbn"] = pd.to_numeric(book["Isbn"], errors="coerce")
# book['Title'] = book['Title'].astype(str).str.strip('"').str.strip()
book["Title"] = book["Title"].astype(str).str.strip().str.strip('"').str.strip()
book = book.dropna(subset=["Isbn"])  # drop rows with empty ISBN
book = book.drop_duplicates(subset=["Isbn"])

# Cleaning up book_authors csv
book_authors["Isbn"] = pd.to_numeric(book_authors["Isbn"], errors="coerce")
book_authors["Author_id"] = pd.to_numeric(book_authors["Author_id"], errors="coerce")
book_authors = book_authors.dropna(subset=["Isbn", "Author_id"])
book_authors["Author_id"] = book_authors["Author_id"].astype(int)
book_authors["Isbn"] = book_authors["Isbn"].astype(int)

# cleaning authors csv
authors["Author_id"] = pd.to_numeric(authors["Author_id"], errors="coerce")
authors = authors.dropna(subset=["Author_id", "Name"])
authors["Author_id"] = authors["Author_id"].astype(int)
# Trim leading/trailing whitespace from names
authors["Name"] = authors["Name"].astype(str).str.strip()
authors = authors.drop_duplicates(subset=["Author_id"])

# cleaning borrower csv
borrower["Card_id"] = borrower["Card_id"].astype(str).str.strip()
borrower = borrower.dropna(subset=["Card_id", "SSN", "First_name", "Last_name"])
borrower = borrower.drop_duplicates(subset=["Card_id"])

#  Insert data into database
book.to_sql("BOOK", conn, if_exists="replace", index=False)
authors.to_sql("AUTHORS", conn, if_exists="replace", index=False)
book_authors.to_sql("BOOK_AUTHORS", conn, if_exists="replace", index=False)
borrower.to_sql("BORROWER", conn, if_exists="replace", index=False)

# Committing and closing the database
conn.commit()
conn.close()

print("Database successfully created")
