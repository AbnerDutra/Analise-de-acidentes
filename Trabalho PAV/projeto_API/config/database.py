import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def create_session_factory() -> sessionmaker:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "A variável de ambiente DATABASE_URL precisa conter a URL do PostgreSQL."
        )

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    engine = create_engine(database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
