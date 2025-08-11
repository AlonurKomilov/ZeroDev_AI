from sqlmodel import create_engine, SQLModel, Session
from backend.core.settings import settings

# The database URL is configured in the central settings.
DATABASE_URL = settings.DATABASE_URL

# Create the database engine
# connect_args is for SQLite. For PostgreSQL, it's not needed.
# I'll add a check for sqlite.
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

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
