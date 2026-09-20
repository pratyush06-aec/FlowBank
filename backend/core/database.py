import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Use Neon DB URL from environment, fallback to local SQLite for quick dev without internet
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bankos.db")

connect_args = {}
if "postgresql" in SQLALCHEMY_DATABASE_URL:
    # Neon DB connection pooling and SSL requirements
    connect_args = {"sslmode": "require"}
elif "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
