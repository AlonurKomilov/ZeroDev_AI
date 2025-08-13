from sqlmodel import create_engine, SQLModel, Session
from backend.core.settings import settings

# The database URL is configured in the central settings.
DATABASE_URL = settings.DATABASE_URL

# Create the database engine
engine = create_engine(settings.DATABASE_URL, echo=True)

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
