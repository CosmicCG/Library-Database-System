# Author: Josh McKone
# Team Fluorine
# Course: CS4347
# Assignment: Database Project - Deliverable 1

# Class definitions
class Book:
  isbn: str
  title: str

  def __init__(self, isbn: str, title: str):
    self.isbn = isbn
    self.title = title

class Author:
  author_id: int
  name: str

  def __init__(self, author_id: int, name: str):
    self.author_id = author_id
    self.name = name

class Book_Author:
  author_id: int
  isbn: str

  def __init__(self, isbn: str, author_id: int):
    self.isbn = isbn
    self.author_id = author_id

# Code beginning
fileObj = open('books.csv', 'r', encoding="utf-8")
text = fileObj.read()

authorcsv = open('authors.csv', 'w', encoding="utf-8")
bookcsv = open('book.csv', 'w', encoding="utf-8")
book_authorcsv = open('book_authors.csv', 'w', encoding="utf-8")

# List creations
books = []
authors_list = []
books_authors = []

current_id = 0
author_set = dict()

# Code for reading in the lines and turning them into usable data
# NOTE: This uses the mopified and cleaned up version of the books.csv where instead of tabs, it uses ','
# And instead of ',' to separate authors, it uses the ';' character instead
for line in text.split('\n'):
  column_list = line.split(',')
  isbn10 = column_list[0]
  isbn13 = column_list[1]
  title = column_list[2]
  authors = column_list[3]
  books.append(Book(isbn13, title))
  # This next line splits the authors (separated by commas) into multiple atomic values
  author_list = authors.split(';')
  for author in author_list:
    if author not in author_set:
      current_id += 1
      author_set[author] = current_id
      authors_list.append(Author(current_id, author))
    books_authors.append(Book_Author(isbn13, author_set[author]))

# Analyzes the data and then writes it out at once
# Also allows for future analysis and cleanups
authorcsv.write('Author_id,Name\n')
for author in authors_list:
  authorcsv.write(f'{author.author_id},{author.name}\n')

bookcsv.write('Isbn,Title\n')
for book in books:
  bookcsv.write(f'{book.isbn},{book.title}\n')

book_authorcsv.write('Author_id,Isbn\n')
for ba in books_authors:
  book_authorcsv.write(f'{ba.author_id},{ba.isbn}\n')
