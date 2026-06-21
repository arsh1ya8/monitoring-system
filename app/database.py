import os
import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv(override=False)

DB_SERVER   = os.environ.get("DB_SERVER", "sqlserver-service")
DB_NAME     = os.environ.get("DB_NAME", "monitoringdb")
DB_USER     = os.environ.get("DB_USER", "sa")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Monitor123456")

CONNECTION_STRING = f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_NAME}"

engine = create_engine(CONNECTION_STRING, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def wait_for_db(retries=15, delay=5):
    for i in range(retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logging.info("Database connection successful!")
            return True
        except Exception as e:
            logging.warning(f"DB not ready ({i+1}/{retries}): {e}")
            time.sleep(delay)
    return False

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
