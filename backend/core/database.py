from backend.core.settings import settings
from sqlmodel import Session, SQLModel, create_engine

# The database URL is configured in the central settings.
DATABASE_URL = settings.DATABASE_URL

# Create the database engine
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def get_session():
    """
    Dependency to get a database session.
    """
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """
    Creates all tables in the database.
    This is useful for initial setup and for tests.
    Alembic will handle migrations for production.
    """
    SQLModel.metadata.create_all(engine)
