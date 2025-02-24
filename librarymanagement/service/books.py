from collections import defaultdict
from typing import List

from librarymanagement.core.settings import settings
from librarymanagement.service.schema import BookListResponse, BookGenre, Book


def group_books_by_genre(books: List[Book]) -> BookListResponse:
    genres = defaultdict(lambda: BookGenre(books=[]))
    for book in books:
        genres[book.genre].books.append(book)

    return BookListResponse(genres=genres)


def mask_title(book: Book) -> Book:
    if book.genre in settings.masked_genres:
        book.title = "*" * 10
    return book


def mask_titles(books: List[Book]) -> List[Book]:
    return [mask_title(book) for book in books]
