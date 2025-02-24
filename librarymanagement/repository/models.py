from sqlalchemy.orm import Mapped, mapped_column

from librarymanagement.repository.database import Base


class BookORM(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    publication_year: Mapped[int] = mapped_column(nullable=False)
    genre: Mapped[str] = mapped_column(nullable=False)

    def __eq__(self, other):
        return (
            isinstance(other, BookORM)
            and self.id == other.id
            and self.title == other.title
            and self.author == other.author
            and self.publication_year == other.publication_year
            and self.genre == other.genre
        )
