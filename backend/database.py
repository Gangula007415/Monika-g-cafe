from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# create a function that will be used to get a database session, which will be used in the API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def auto_migrate_schema():
    try:
        inspector = inspect(engine)
        if inspector.has_table("users"):
            existing_columns = [c["name"] for c in inspector.get_columns("users")]
            with engine.begin() as conn:
                if "failed_login_attempts" not in existing_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN failed_login_attempts INT DEFAULT 0 NULL"))
                if "locked_until" not in existing_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN locked_until DATETIME NULL"))
    except Exception as e:
        print(f"Auto-migration warning: {e}")