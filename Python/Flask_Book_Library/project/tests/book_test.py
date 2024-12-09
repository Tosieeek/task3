import pytest
from project.books.models import Book
from sqlalchemy.exc import DataError


@pytest.mark.parametrize("title, writer, publication_year, genre", [
    ("Dune", "Frank Herbert", 1965, "Science Fiction"),
    ("The Road", "Cormac McCarthy", 2006, "Post-Apocalyptic"),
    ("Hyperion", "Dan Simmons", 1989, "Space Opera"),
    ("Neverwhere", "Neil Gaiman", 1996, "Urban Fantasy"),
    ("Good Omens", "Terry Pratchett & Neil Gaiman", 1990, "Comedy Fantasy"),
    ("Mistborn", "Brandon Sanderson", 2006, "Epic Fantasy"),
])
def test_creation_valid_input(title, writer, publication_year, genre):
    book = Book(name=title, author=writer, year_published=publication_year, book_type=genre)

    assert book.name == title
    assert book.author == writer
    assert book.year_published == publication_year
    assert book.book_type == genre


@pytest.mark.parametrize("title, writer, publication_year, genre", [
    ("", "Frank Herbert", 1965, "Science Fiction"),
    (None, "Cormac McCarthy", 2006, "Post-Apocalyptic"),
    ("D" * 101, "Dan Simmons", 1989, "Space Opera"),
    ("Dune", "", 1965, "Science Fiction"),
    ("The Road", None, 2006, "Post-Apocalyptic"),
    ("Hyperion", "A" * 101, 1989, "Space Opera"),
    ("1984", "George Orwell", 1949, ""),
    ("Neverwhere", "Neil Gaiman", 1996, None),
    ("Mistborn", "Brandon Sanderson", 2006, "G" * 51),
    ("", "", -1, ""),
    (None, None, None, None),
])
def test_creation_invalid_input(title, writer, publication_year, genre):
    with pytest.raises(DataError):
        book = Book(name=title, author=writer, year_published=publication_year, book_type=genre)


@pytest.mark.parametrize("title, writer, publication_year, genre", [
    ("' OR '1'='1", "Frank Herbert", 1965, "Science Fiction"),
    ("Dune", "'; DROP TABLE books; --", 1965, "Science Fiction"),
    ("Hyperion", "Dan Simmons", "1; EXEC xp_cmdshell('dir')", "Space Opera"),
    ("The Book Thief", "Markus Zusak", 2005, "'; DELETE FROM genres; --"),
])
def test_sql_injection_prevention(title, writer, publication_year, genre):
    with pytest.raises(DataError):
        book = Book(name=title, author=writer, year_published=publication_year, book_type=genre)


@pytest.mark.parametrize("title, writer, publication_year, genre", [
    ("<script>alert(1)</script>", "Frank Herbert", 1965, "Science Fiction"),
    ("Dune", "<svg onload=alert('1')>", 1965, "Science Fiction"),
    ("Hyperion222", "Dan Simmons", 1989, "<img src=x onerror=alert('1')>"),
    ("The Book Thief", "Markus Zusak", 2005, "<script>alert(1)</script>"),
])
def test_xss_injection(title, writer, publication_year, genre):
    with pytest.raises(DataError):
        book = Book(name=title, author=writer, year_published=publication_year, book_type=genre)


@pytest.mark.parametrize("title, writer, publication_year, genre", [
    ("A" * 1000000, "Frank Herbert", 1965, "Science Fiction"),
    ("Dune", "!" * 100000, 1965, "Science Fiction"),
    ("Hyperion", "Dan Simmons", -999999, "Space Opera"),
    ("The Book Thief", "Markus Zusak", 2005, "G" * 100000),
])
def test_extreme_values(title, writer, publication_year, genre):
    with pytest.raises(DataError):
        book = Book(name=title, author=writer, year_published=publication_year, book_type=genre)