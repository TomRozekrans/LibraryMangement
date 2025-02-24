from unittest.mock import patch

from librarymanagement.core.settings import settings
from librarymanagement.service.books import group_books_by_genre, mask_title, mask_titles
from librarymanagement.service.schema import Book, BookListResponse, BookGenre


def test_group_books_by_genre():
    books = [
        Book(
            id=10,
            title="The Great Gatsby",
            genre="Fiction",
            author="F. Scott Fitzgerald",
            publication_year=1925,
        ),
        Book(
            id=11,
            title="The Da Vinci Code",
            genre="Thriller",
            author="Dan Brown",
            publication_year=2003,
        ),
        Book(
            id=12,
            title="The Catcher in the Rye",
            genre="Fiction",
            author="J. D. Salinger",
            publication_year=1951,
        ),
        Book(
            id=13,
            title="The Hobbit",
            genre="Fantasy",
            author="J. R. R. Tolkien",
            publication_year=1937,
        ),
        Book(
            id=14,
            title="The Hunger Games",
            genre="Science Fiction",
            author="Suzanne Collins",
            publication_year=2008,
        ),
        Book(
            id=15,
            title="Harry Potter and the Philosopher's Stone",
            genre="Fantasy",
            author="J. K. Rowling",
            publication_year=1997,
        ),
    ]

    expected = BookListResponse(
        genres={
            "Fiction": BookGenre(
                books=[
                    Book(
                        id=10,
                        title="The Great Gatsby",
                        genre="Fiction",
                        author="F. Scott Fitzgerald",
                        publication_year=1925,
                    ),
                    Book(
                        id=12,
                        title="The Catcher in the Rye",
                        genre="Fiction",
                        author="J. D. Salinger",
                        publication_year=1951,
                    ),
                ]
            ),
            "Thriller": BookGenre(
                books=[
                    Book(
                        id=11,
                        title="The Da Vinci Code",
                        genre="Thriller",
                        author="Dan Brown",
                        publication_year=2003,
                    ),
                ]
            ),
            "Fantasy": BookGenre(
                books=[
                    Book(
                        id=13,
                        title="The Hobbit",
                        genre="Fantasy",
                        author="J. R. R. Tolkien",
                        publication_year=1937,
                    ),
                    Book(
                        id=15,
                        title="Harry Potter and the Philosopher's Stone",
                        genre="Fantasy",
                        author="J. K. Rowling",
                        publication_year=1997,
                    ),
                ]
            ),
            "Science Fiction": BookGenre(
                books=[
                    Book(
                        id=14,
                        title="The Hunger Games",
                        genre="Science Fiction",
                        author="Suzanne Collins",
                        publication_year=2008,
                    ),
                ]
            ),
        }
    )

    grouped_books = group_books_by_genre(books)

    assert grouped_books == expected


def test_group_books_by_genre_empty():
    books = []

    expected = BookListResponse(genres={})

    grouped_books = group_books_by_genre(books)

    assert grouped_books == expected


def test_mask_title():
    settings.masked_genres = ["Fiction"]

    book = Book(
        id=10,
        title="The Great Gatsby",
        genre="Fiction",
        author="F. Scott Fitzgerald",
        publication_year=1925,
    )

    expected = Book(
        id=10,
        title="**********",
        genre="Fiction",
        author="F. Scott Fitzgerald",
        publication_year=1925,
    )

    masked_book = mask_title(book)

    assert masked_book == expected


def test_mask_titles():
    books = [
        Book(
            id=10,
            title="The Great Gatsby",
            genre="Fiction",
            author="F. Scott Fitzgerald",
            publication_year=1925,
        ),
        Book(
            id=11,
            title="The Da Vinci Code",
            genre="Thriller",
            author="Dan Brown",
            publication_year=2003,
        ),
    ]

    with patch("librarymanagement.service.books.mask_title") as mock_mask_title:
        mock_mask_title.side_effect = [
            Book(
                id=10,
                title="**********",
                genre="Fiction",
                author="F. Scott Fitzgerald",
                publication_year=1925,
            ),
            Book(
                id=11,
                title="The Da Vinci Code",
                genre="Thriller",
                author="Dan Brown",
                publication_year=2003,
            ),
        ]
        masked_books = mask_titles(books)

        expected = [
            Book(
                id=10,
                title="**********",
                genre="Fiction",
                author="F. Scott Fitzgerald",
                publication_year=1925,
            ),
            Book(
                id=11,
                title="The Da Vinci Code",
                genre="Thriller",
                author="Dan Brown",
                publication_year=2003,
            ),
        ]

        assert masked_books == expected
        assert mock_mask_title.call_count == 2
        mock_mask_title.assert_any_call(books[0])
        mock_mask_title.assert_any_call(books[1])
