from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def verify_connection():
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            print("[SUCCESS] Connected successfully to:", version)
    except Exception as e:
        print("[ERROR] Connection failed:", e)

def execute_sql(sql_query: str):
    try:
        with next(get_session()) as session:
            result = session.execute(text(sql_query))
            return [dict(row) for row in result.mappings()]
    except Exception as e:
        print("[ERROR] SQL execution failed:", e)
        return []
