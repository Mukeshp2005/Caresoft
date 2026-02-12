from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

try:
    load_dotenv()
except OSError:
    # On some systems (like macOS with Docker bind mounts), this can fail with 
    # "Resource deadlock avoided" (Errno 35). We ignore it since environment 
    # variables are often already set via docker-compose.
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://caresoft_user:caresoft_password@localhost:5432/caresoft_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
