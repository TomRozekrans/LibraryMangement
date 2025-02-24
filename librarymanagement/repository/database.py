from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

engine = create_engine("sqlite:///library.db", echo=True, connect_args={"check_same_thread": False})

Base = declarative_base()


def get_session():
    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
