import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_SERVER   = os.getenv("DB_SERVER", "sqlserver")
DB_NAME     = os.getenv("DB_NAME", "monitoringdb")
DB_USER     = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "YourPassword123!")

CONNECTION_STRING = f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_NAME}"

engine = create_engine(CONNECTION_STRING, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
