from contextlib import asynccontextmanager

from fastapi import FastAPI
from librarymanagement.controller.librarymanager import book_router
from librarymanagement.repository.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # Create tables
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(book_router, prefix="/books", tags=["books"])
