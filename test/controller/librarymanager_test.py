from unittest.mock import patch, MagicMock, ANY

import pytest
from starlette.testclient import TestClient

from librarymanagement.core.exeptions import InvalidBookIdException, LastBookGenreDeleteException
from librarymanagement.core.settings import settings
from librarymanagement.main import app
from librarymanagement.repository.database import get_session
from librarymanagement.service.schema import (
    Book,
    NewBook,
    UpdateBook,
    BookListResponse,
    BookGenre,
)


def override_get_session():
    return MagicMock()


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


TEST_BOOKS = [
    Book(id=0, title="Book 1", author="Author 1", genre="Genre 1", publication_year=2020),
    Book(id=1, title="Book 2", author="Author 2", genre="Genre 2", publication_year=2021),
    Book(id=2, title="Book 3", author="Author 3", genre="Genre 3", publication_year=2022),
]


def test_get_books(client):
    with patch(
        "librarymanagement.controller.librarymanager.get_all_books",
        return_value=TEST_BOOKS,
    ) as mock_get_all_books:
        with patch(
            "librarymanagement.controller.librarymanager.mask_titles",
            return_value=TEST_BOOKS,
        ) as mock_mask_titles:
            response = client.get("/books")
            assert response.status_code == 200
            assert response.json() == [book.model_dump() for book in TEST_BOOKS]
            mock_get_all_books.assert_called_once_with(ANY)
            mock_mask_titles.assert_called_once_with(TEST_BOOKS)


def test_get_books_with_filter(client):
    settings.disabled_genres_search = ["Genre 1"]

    with patch(
        "librarymanagement.controller.librarymanager.get_all_books",
        return_value=TEST_BOOKS,
    ) as mock_get_all_books:
        with patch(
            "librarymanagement.controller.librarymanager.mask_titles",
            return_value=TEST_BOOKS,
        ) as mock_mask_titles:
            response = client.get("/books", params={"title": "Book 1", "author": "Author 1"})
            assert response.status_code == 200
            assert response.json() == [book.model_dump() for book in TEST_BOOKS]
            mock_get_all_books.assert_called_once_with(
                ANY, title="Book 1", author="Author 1", excluded_genres=["Genre 1"]
            )
            mock_mask_titles.assert_called_once_with(TEST_BOOKS)


def test_create_book(client):
    settings.disabled_genres_create = ["Genre 2"]

    with patch(
        "librarymanagement.controller.librarymanager.insert_book",
        return_value=TEST_BOOKS[0],
    ) as mock_create_book:
        response = client.post("/books", json=TEST_BOOKS[0].model_dump(exclude={"id"}))

        assert response.status_code == 200
        assert response.json() == TEST_BOOKS[0].model_dump()
        mock_create_book.assert_called_once_with(ANY, NewBook.model_validate(TEST_BOOKS[0], from_attributes=True))


def test_create_book_disabled_genre(client):
    settings.disabled_genres_create = ["Genre 1"]

    with patch(
        "librarymanagement.controller.librarymanager.insert_book",
        return_value=TEST_BOOKS[0],
    ) as mock_create_book:
        response = client.post("/books", json=TEST_BOOKS[0].model_dump(exclude={"id"}))

        assert response.status_code == 400
        assert response.json() == {"detail": "Cannot create book in the genre Genre 1"}
        mock_create_book.assert_not_called()


def test_update_book(client):
    settings.disabled_genres_create = ["Genre 2"]

    with patch(
        "librarymanagement.controller.librarymanager.update_books",
        return_value=[TEST_BOOKS[1]],
    ) as mock_update_book:
        response = client.patch("/books/", json=[TEST_BOOKS[0].model_dump()])

        assert response.status_code == 200
        assert response.json() == [TEST_BOOKS[1].model_dump()]
        mock_update_book.assert_called_once_with(ANY, [UpdateBook.model_validate(TEST_BOOKS[0], from_attributes=True)])


def test_update_book_disabled_genre(client):
    settings.disabled_genres_create = ["Genre 1"]

    with patch("librarymanagement.controller.librarymanager.update_books") as mock_update_book:
        response = client.patch("/books/", json=[TEST_BOOKS[0].model_dump()])

        assert response.status_code == 400
        assert response.json() == {"detail": "Cannot change genre of book to Genre 1"}
        mock_update_book.assert_not_called()


def test_update_book_invalid_id(client):
    settings.disabled_genres_create = ["Genre 2"]

    with patch(
        "librarymanagement.controller.librarymanager.update_books",
    ) as mock_update_book:
        mock_update_book.side_effect = InvalidBookIdException(100)

        response = client.patch("/books/", json=[TEST_BOOKS[0].model_dump()])

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid book id: 100"}
        mock_update_book.assert_called_once_with(ANY, [UpdateBook.model_validate(TEST_BOOKS[0], from_attributes=True)])


def test_get_books_by_genre(client):
    grouped_books = BookListResponse(genres={"Genre 3": BookGenre(books=[TEST_BOOKS[2]])})

    with patch(
        "librarymanagement.controller.librarymanager.get_all_books",
        return_value=[TEST_BOOKS[0]],
    ) as mock_get_all_books:
        with patch(
            "librarymanagement.controller.librarymanager.mask_titles",
            return_value=[TEST_BOOKS[1]],
        ) as mock_mask_titles:
            with patch(
                "librarymanagement.controller.librarymanager.group_books_by_genre",
                return_value=grouped_books,
            ) as mock_group_books_by_genre:
                response = client.get("/books/group_by_genre")

                assert response.status_code == 200
                assert response.json() == grouped_books.model_dump()

                mock_get_all_books.assert_called_once_with(ANY)
                mock_mask_titles.assert_called_once_with([TEST_BOOKS[0]])
                mock_group_books_by_genre.assert_called_once_with([TEST_BOOKS[1]])


def test_get_book(client):
    with patch(
        "librarymanagement.controller.librarymanager.get_book_by_id",
        return_value=TEST_BOOKS[0],
    ) as mock_get_book:
        response = client.get("/books/0")

        assert response.status_code == 200
        assert response.json() == TEST_BOOKS[0].model_dump()
        mock_get_book.assert_called_once_with(ANY, 0)


def test_get_book_invalid_id(client):
    with patch("librarymanagement.controller.librarymanager.get_book_by_id") as mock_get_book:
        mock_get_book.side_effect = InvalidBookIdException(100)

        response = client.get("/books/100")

        assert response.status_code == 404
        assert response.json() == {"detail": "Invalid book id: 100"}
        mock_get_book.assert_called_once_with(ANY, 100)


def test_delete_book(client):
    with patch(
        "librarymanagement.controller.librarymanager.delete_book_by_id",
        return_value=TEST_BOOKS[0],
    ) as mock_delete_book:
        response = client.delete("/books/0")

        assert response.status_code == 204
        mock_delete_book.assert_called_once_with(ANY, 0)


def test_delete_book_invalid_id(client):
    with patch("librarymanagement.controller.librarymanager.delete_book_by_id") as mock_delete_book:
        mock_delete_book.side_effect = InvalidBookIdException(100)

        response = client.delete("/books/100")

        assert response.status_code == 404
        assert response.json() == {"detail": "Invalid book id: 100"}
        mock_delete_book.assert_called_once_with(ANY, 100)


def test_delete_book_last_genre(client):
    with patch(
        "librarymanagement.controller.librarymanager.delete_book_by_id",
    ) as mock_delete_book:
        mock_delete_book.side_effect = LastBookGenreDeleteException(100)

        response = client.delete("/books/100")

        assert response.status_code == 400
        assert response.json() == {"detail": "Last book in genre cannot be deleted: 100"}
        mock_delete_book.assert_called_once_with(ANY, 100)
