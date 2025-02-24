import pytest

from librarymanagement.core.exeptions import InvalidBookIdException, LastBookGenreDeleteException


def test_invalid_book_id_exception():
    with pytest.raises(InvalidBookIdException) as execinfo:
        raise InvalidBookIdException(10)

    assert "10" in str(execinfo.value)


def test_last_book_genre_delete_execption():
    with pytest.raises(LastBookGenreDeleteException) as execinfo:
        raise LastBookGenreDeleteException(10)

    assert "10" in str(execinfo.value)
