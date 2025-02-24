from typing import Optional

from pydantic import BaseModel, computed_field


class NewBook(BaseModel):
    title: str
    author: str
    publication_year: int
    genre: str


class Book(BaseModel):
    id: int
    title: str
    author: str
    publication_year: int
    genre: str


class UpdateBook(BaseModel):
    id: int
    title: Optional[str] = None
    author: Optional[str] = None
    publication_year: Optional[int] = None
    genre: Optional[str] = None


class BookGenre(BaseModel):
    books: list[Book]

    @computed_field
    @property
    def count(self) -> int:
        return len(self.books)


class BookListResponse(BaseModel):
    genres: dict[str, BookGenre]
