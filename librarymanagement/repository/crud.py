from typing import Optional, List

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from librarymanagement.core.exeptions import InvalidBookIdException, LastBookGenreDeleteException
from librarymanagement.repository.models import BookORM
from librarymanagement.service.schema import Book, NewBook, UpdateBook


def get_all_books(
    db: Session,
    author: Optional[str] = None,
    title: Optional[str] = None,
    excluded_genres=None,
) -> List[Book]:
    filters = []
    if author:
        filters.append(BookORM.author.ilike(f"%{author}%"))
    if title:
        filters.append(BookORM.title.ilike(f"%{title}%"))

    query = select(BookORM)

    if filters:
        query = query.filter(or_(*filters))

    if excluded_genres:
        query = query.filter(~BookORM.genre.in_(excluded_genres))

    query_result = db.execute(query).scalars().all()
    return [Book.model_validate(row, from_attributes=True) for row in query_result]


def get_book_by_id(db: Session, book_id: int) -> Book:
    query_result = db.execute(select(BookORM).filter(BookORM.id == book_id)).scalar_one_or_none()
    if not query_result:
        raise InvalidBookIdException(book_id)
    return Book.model_validate(query_result, from_attributes=True)


def insert_book(db: Session, book: NewBook) -> Book:
    book_orm = BookORM(**book.model_dump())
    db.add(book_orm)
    db.commit()

    return Book.model_validate(book_orm, from_attributes=True)


def update_books(db: Session, books: list[UpdateBook]) -> list[Book]:
    db.begin()
    updated_books = []
    for book in books:
        book_orm = db.execute(select(BookORM).filter(BookORM.id == book.id)).scalar_one_or_none()
        if not book_orm:
            db.rollback()
            raise InvalidBookIdException(book.id)
        for key, value in book.model_dump(exclude="id").items():
            if value is not None:
                setattr(book_orm, key, value)
        updated_books.append(book_orm)
    db.commit()

    return [Book.model_validate(book, from_attributes=True) for book in updated_books]


def delete_book_by_id(db: Session, book_id: int):
    book_orm = db.execute(select(BookORM).filter(BookORM.id == book_id)).scalar_one_or_none()
    if not book_orm:
        raise InvalidBookIdException(book_id)
    count = db.execute(select(func.count()).select_from(BookORM).where(BookORM.genre == book_orm.genre)).scalar()
    if count == 1:
        raise LastBookGenreDeleteException(book_id)
    db.delete(book_orm)
    db.commit()
