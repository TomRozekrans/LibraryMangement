import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from librarymanagement.core.exeptions import InvalidBookIdException, LastBookGenreDeleteException
from librarymanagement.core.settings import settings
from librarymanagement.repository.crud import (
    get_all_books,
    insert_book,
    update_books,
    get_book_by_id,
    delete_book_by_id,
)
from librarymanagement.repository.database import SessionDependency
from librarymanagement.service.books import group_books_by_genre, mask_titles, mask_title
from librarymanagement.service.schema import BookListResponse, Book, NewBook, UpdateBook


logger = logging.getLogger(__name__)

book_router = APIRouter()


@book_router.get("/")
def get_books(
    session: SessionDependency,
    author: Optional[str] = None,
    title: Optional[str] = None,
) -> list[Book]:
    if author or title:
        books = get_all_books(
            session,
            author=author,
            title=title,
            excluded_genres=settings.disabled_genres_search,
        )
    else:
        books = get_all_books(session)
    masked_books = mask_titles(books)
    return masked_books


@book_router.post("/")
def create_book(session: SessionDependency, book: NewBook) -> Book:
    if book.genre in settings.disabled_genres_create:
        logger.info(f"Cannot create book in the genre {book.genre}")
        raise HTTPException(status_code=400, detail=f"Cannot create book in the genre {book.genre}")
    return insert_book(session, book)


@book_router.patch("/")
def update_book(session: SessionDependency, books: list[UpdateBook]) -> list[Book]:
    for book in books:
        if book.genre in settings.disabled_genres_create:
            logger.info(f"Cannot change genre of book to {book.genre}")
            raise HTTPException(status_code=400, detail=f"Cannot change genre of book to {book.genre}")

    try:
        updated_books = update_books(session, books)
        return mask_titles(updated_books)
    except InvalidBookIdException as e:
        raise HTTPException(status_code=400, detail=str(e))


@book_router.get("/group_by_genre")
def get_books_group_by_genre(
    session: SessionDependency,
    author: Optional[str] = None,
    title: Optional[str] = None,
) -> BookListResponse:
    if author or title:
        books = get_all_books(
            session,
            author=author,
            title=title,
            excluded_genres=settings.disabled_genres_search,
        )
    else:
        books = get_all_books(session)
    masked_books = mask_titles(books)
    return group_books_by_genre(masked_books)


@book_router.get("/{book_id}")
def get_book(session: SessionDependency, book_id: int) -> Book:
    try:
        book = get_book_by_id(session, book_id)
    except InvalidBookIdException as e:
        logger.info(f"Book with id {book_id} not found, {e}")
        raise HTTPException(status_code=404, detail=str(e))
    return mask_title(book)


@book_router.delete("/{book_id}", status_code=204)
def delete_book(session: SessionDependency, book_id: int) -> None:
    try:
        delete_book_by_id(session, book_id)
    except InvalidBookIdException as e:
        logger.info(f"Book with id {book_id} not found, {e}")
        raise HTTPException(status_code=404, detail=str(e))

    except LastBookGenreDeleteException as e:
        logger.info(f"Cannot delete the last book in genre, {e}")
        raise HTTPException(status_code=400, detail=str(e))
