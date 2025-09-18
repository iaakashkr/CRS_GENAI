from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# PostgreSQL credentials (fill these in)
DB_USER = "xyz"
DB_PASSWORD = "xyz"
DB_HOST = "productsxyz"          # or your server IP
DB_PORT = "5002"
DB_NAME = "xyz"

# Create connection string
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)  
# pool_pre_ping=True ensures connections are alive

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Context manager to automatically close sessions
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Helper: verify connection
def verify_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connection successful, test query result:", result.scalar())
    except Exception as e:
        print("❌ Connection failed:", e)

# Execute SQL helper
def execute_sql(sql_query: str):
    """Execute SQL and return list of dicts."""
    try:
        with next(get_session()) as session:
            result = session.execute(text(sql_query))
            # Use .mappings() to get dictionaries instead of row tuples
            return [dict(row) for row in result.mappings()]
    except Exception as e:
        print("❌ SQL execution failed:", e)
        return []

