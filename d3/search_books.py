import sqlite3


def search_books(keyword, conn: sqlite3.Connection):
  cursor = conn.cursor()
  queryBooks = """
    SELECT
      b.Isbn,
      b.Title,
      GROUP_CONCAT(a.Name, ', ') Authors,
      Case
        WHEN EXISTS (
          SELECT 1 FROM BOOK_LOANS bl
          WHERE bl.Isbn = b.Isbn AND bl.Date_in IS NULL
        ) THEN 'OUT'
        ELSE 'IN'
      END AS Status
    FROM BOOK_AUTHORS ba
    JOIN BOOK b ON ba.Isbn = b.Isbn
    JOIN AUTHORS a ON ba.Author_id = a.Author_id
    WHERE
      LOWER(b.Title) LIKE ?
      OR LOWER(a.Name) LIKE ?
      OR b.Isbn LIKE ?
    GROUP BY b.Isbn
    ORDER BY b.Title, Authors;
    """
  kw = f"%{keyword.lower().strip()}%"
  cursor.execute(queryBooks, (kw, kw, kw))
  results = cursor.fetchall()

  if not results:
    print(f"\nNo matches found for '{keyword}'.\n")
    return []
  print("\nSearch Results:")
  print("{:<15} {:<150} {:<50} {:<5}".format("ISBN", "Title", "Author", "Status"))
  print("-" * 220)
  for isbn, title, author, status in results:
    print(f"{isbn:<15} {title:<150} {author:<50} {status:<5}")
  print()

  return results
