import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

def get_engine():
    db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    is_cloud = os.getenv("RENDER") is not None or "onrender.com" in os.getenv("RENDER_EXTERNAL_URL", "")
    
    # If running on Render cloud and no external DATABASE_URL was supplied (still points to localhost),
    # use SQLite directly to ensure fast, clean startup without connection timeouts.
    if is_cloud and "localhost" in db_url:
        print("ℹ️ Running on Render cloud. Using SQLite database for zero-config persistence.")
        return create_engine("sqlite:///./monika_cafe.db", connect_args={"check_same_thread": False})
        
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    if "sqlite" in db_url:
        return create_engine(db_url, connect_args={"check_same_thread": False})

    try:
        eng = create_engine(db_url, pool_pre_ping=True)
        with eng.connect() as conn:
            pass
        return eng
    except Exception as e:
        print(f"ℹ️ Primary DB unavailable ({e}). Using SQLite database.")
        sqlite_url = "sqlite:///./monika_cafe.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_engine()
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

        if inspector.has_table("roles"):
            with engine.begin() as conn:
                res = conn.execute(text("SELECT COUNT(*) FROM roles")).scalar()
                if res == 0:
                    conn.execute(text("INSERT INTO roles (role_id, role_name) VALUES (1, 'Admin'), (2, 'Customer'), (3, 'Employee'), (4, 'Manager')"))
    except Exception as e:
        print(f"Auto-migration warning: {e}")
