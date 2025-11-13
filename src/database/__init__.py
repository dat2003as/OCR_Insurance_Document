"""
Database Configuration and Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from src.settings import APP_SETTINGS
from typing import Generator

# Create declarative base
Base = declarative_base()

# Create engine
engine = None
SessionLocal = None

def init_database():
    """Initialize database connection"""
    global engine, SessionLocal
    
    # Get database URL from settings
    database_url =APP_SETTINGS.DATABASE_URL
    
    # Fallback to SQLite if no DATABASE_URL
    # if not database_url:
    #     database_url = "sqlite:///./ocr_medical.db"
    #     print(f"⚠️  DATABASE_URL not set, using SQLite: {database_url}")
    
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False  # Set to True for SQL logging
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine

def init_db():
    """Initialize database tables"""
    from src.database.models import Base
    
    if engine is None:
        init_database()
    
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

def get_db() -> Generator[Session, None, None]:
    """
    Get database session
    Use as dependency injection in FastAPI:
    
    @app.get("/items")
    def get_items(db: Session = Depends(get_db)):
        ...
    """
    if SessionLocal is None:
        init_database()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize on import
init_database()
init_db()