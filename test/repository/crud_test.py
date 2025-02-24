import pytest
from sqlalchemy import select, create_engine, func
from sqlalchemy.orm import sessionmaker

from librarymanagement.core.exeptions import InvalidBookIdException, LastBookGenreDeleteException
from librarymanagement.repository.crud import (
    get_all_books,
    get_book_by_id,
    insert_book,
    update_books,
    delete_book_by_id,
)
from librarymanagement.repository.database import Base
from librarymanagement.repository.models import BookORM
from librarymanagement.service.schema import Book, NewBook, UpdateBook


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)  # Create tables

    session = TestingSessionLocal()

    try:
        print("Creating session")
        yield session  # Provide the session to the test
    finally:
        session.close()
        Base.metadata.drop_all(engine)  # Clean up after test


TEST_BOOKS = [
    Book(id=0, title="Book 1", author="Author 1", genre="Genre 1", publication_year=2021),
    Book(id=1, title="Book 2", author="Author 2", genre="Genre 2", publication_year=2022),
    Book(id=2, title="Book 3", author="Author 3", genre="Genre 3", publication_year=2023),
    Book(
        id=3,
        title="Book 4 aaa",
        author="Author 4",
        genre="Genre 3",
        publication_year=2024,
    ),
    Book(
        id=4,
        title="Book 5 aaa",
        author="Author 5",
        genre="Genre 3",
        publication_year=2025,
    ),
    Book(
        id=5,
        title="Book 6 aaa",
        author="Author 5",
        genre="Genre 3",
        publication_year=2026,
    ),
    Book(
        id=6,
        title="Book 7 aaa",
        author="Author 5",
        genre="Genre 4",
        publication_year=2027,
    ),
    Book(id=7, title="Book 8", author="Author 5", genre="Genre 5", publication_year=2028),
]


def orm_books(books: list[Book]) -> list[BookORM]:
    return [
        BookORM(
            id=book.id,
            title=book.title,
            author=book.author,
            genre=book.genre,
            publication_year=book.publication_year,
        )
        for book in books
    ]


def test_get_all_books(session):
    session.add_all(orm_books(TEST_BOOKS))
    session.commit()

    result = get_all_books(session)

    assert result == TEST_BOOKS


@pytest.mark.parametrize(
    "books, expected, author, title, excluded_genres",
    [
        (TEST_BOOKS, TEST_BOOKS, None, None, None),
        (TEST_BOOKS, TEST_BOOKS[4:8], "Author 5", None, None),
        (TEST_BOOKS, TEST_BOOKS[6:8], "Author 5", None, ["Genre 3"]),
        (TEST_BOOKS, TEST_BOOKS[3:7], None, "aaa", None),
        (TEST_BOOKS, TEST_BOOKS[6:7], None, "aaa", ["Genre 3"]),
        (TEST_BOOKS, TEST_BOOKS[3:8], "Author 5", "aaa", None),
        (TEST_BOOKS, TEST_BOOKS[6:8], "Author 5", "aaa", ["Genre 3"]),
        (TEST_BOOKS, TEST_BOOKS[6:7], "Author 5", "aaa", ["Genre 3", "Genre 5"]),
    ],
)
def test_get_all_books_with_filters(session, books, expected, author, title, excluded_genres):
    session.add_all(orm_books(books))
    session.commit()

    result = get_all_books(session, author=author, title=title, excluded_genres=excluded_genres)

    assert result == expected


def test_get_book_by_id(session):
    session.add_all(orm_books(TEST_BOOKS))
    session.commit()

    result = get_book_by_id(session, 3)

    assert result == TEST_BOOKS[3]


def test_get_book_by_id_not_found(session):
    with pytest.raises(InvalidBookIdException):
        get_book_by_id(session, 100)


def test_insert_book(session):
    newbook = NewBook(title="TEST_NEW_BOOK", author="Author 1", genre="Genre 1", publication_year=2021)

    expected_book = Book(
        id=1,
        title="TEST_NEW_BOOK",
        author="Author 1",
        genre="Genre 1",
        publication_year=2021,
    )
    expected_book_orm = orm_books([expected_book])[0]
    result = insert_book(session, newbook)

    assert result == expected_book
    assert session.execute(select(BookORM).filter(BookORM.id == 1)).scalars().first() == expected_book_orm


def test_update_books(session):
    session.add_all(orm_books(TEST_BOOKS))
    session.commit()

    updated_books = [
        UpdateBook(
            id=0,
            title="updated_title",
            author="updated_author",
            genre="updated_genre",
            publication_year=9990,
        ),
        UpdateBook(
            id=1,
            title="updated_title_1",
            author="updated_author_1",
            genre="updated_genre_1",
            publication_year=9991,
        ),
    ]

    expected_return_value = [
        Book(
            id=0,
            title="updated_title",
            author="updated_author",
            genre="updated_genre",
            publication_year=9990,
        ),
        Book(
            id=1,
            title="updated_title_1",
            author="updated_author_1",
            genre="updated_genre_1",
            publication_year=9991,
        ),
    ]
    expected_return_value_orm = orm_books(expected_return_value)

    result = update_books(session, updated_books)

    assert result == expected_return_value
    assert session.execute(select(BookORM).filter(BookORM.id.in_([0, 1]))).scalars().all() == expected_return_value_orm


def test_update_books_partial(session):
    session.add_all(orm_books(TEST_BOOKS))
    session.commit()

    updated_books = [
        UpdateBook(id=0, title="updated_title", author="updated_author"),
        UpdateBook(id=1, genre="updated_genre_1", publication_year=9991),
    ]

    expected_return_value = [
        Book(
            id=0,
            title="updated_title",
            author="updated_author",
            genre="Genre 1",
            publication_year=2021,
        ),
        Book(
            id=1,
            title="Book 2",
            author="Author 2",
            genre="updated_genre_1",
            publication_year=9991,
        ),
    ]
    expected_return_value_orm = orm_books(expected_return_value)

    result = update_books(session, updated_books)

    assert result == expected_return_value
    assert session.execute(select(BookORM).filter(BookORM.id.in_([0, 1]))).scalars().all() == expected_return_value_orm


def test_update_books_not_found(session):
    session.add_all(orm_books(TEST_BOOKS))
    session.commit()

    updated_books = [
        UpdateBook(
            id=0,
            title="updated_title",
            author="updated_author",
            genre="updated_genre",
            publication_year=9990,
        ),
        UpdateBook(
            id=100,
            title="updated_title_1",
            author="updated_author_1",
            genre="updated_genre_1",
            publication_year=9991,
        ),
    ]

    expected_return_value_orm = orm_books(TEST_BOOKS[:1])
    with pytest.raises(InvalidBookIdException):
        update_books(session, updated_books)

    assert session.execute(select(BookORM).filter(BookORM.id == 0)).scalars().all() == expected_return_value_orm
    assert session.execute(select(func.count()).select_from(BookORM).where(BookORM.id == 100)).scalar() == 0


def test_delete_book_by_id(session):
    session.add_all(orm_books(TEST_BOOKS))
    session.commit()

    delete_book_by_id(session, 3)

    assert session.execute(select(func.count()).select_from(BookORM).where(BookORM.id == 3)).scalar() == 0


def test_delete_book_by_id_not_found(session):
    session.add_all(orm_books(TEST_BOOKS))
    session.commit()

    with pytest.raises(InvalidBookIdException):
        delete_book_by_id(session, 100)

    assert session.execute(select(func.count()).select_from(BookORM)).scalar() == len(TEST_BOOKS)


def test_delete_book_last_genre(session):
    session.add_all(orm_books(TEST_BOOKS))
    session.commit()

    with pytest.raises(LastBookGenreDeleteException):
        delete_book_by_id(session, 0)

    assert session.execute(select(func.count()).select_from(BookORM)).scalar() == len(TEST_BOOKS)
