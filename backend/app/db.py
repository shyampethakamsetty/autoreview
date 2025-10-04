from sqlmodel import create_engine, SQLModel, Session
import os
from urllib.parse import urlparse

# Database configuration with production-ready settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data.db')

# Parse database URL to determine database type
parsed_url = urlparse(DATABASE_URL)
db_type = parsed_url.scheme.split('+')[0]
 
# Configure engine based on database type
if db_type == 'postgresql':
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300
    )
elif db_type == 'sqlite':
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    # Default fallback
    engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
