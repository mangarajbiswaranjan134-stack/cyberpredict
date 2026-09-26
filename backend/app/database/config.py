import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("cyberpredict.database")

# Primary Database URL: PostgreSQL
PG_URL = os.getenv("DATABASE_URL", "postgresql://postgres@localhost:5432/cyberpredict")
SQLITE_URL = "sqlite:///./cyberpredict.db"

Base = declarative_base()

def init_engine():
    """Attempts connection to PostgreSQL; if unavailable, falls back to SQLite."""
    try:
        pg_engine = create_engine(
            PG_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args={"connect_timeout": 3}
        )
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"[DATABASE] Connected to PostgreSQL: {PG_URL.split('@')[-1]}")
        return pg_engine, "POSTGRESQL"
    except Exception as e:
        logger.warning(f"[DATABASE] PostgreSQL not reachable ({e}). Falling back to SQLite: {SQLITE_URL}")
        sqlite_engine = create_engine(
            SQLITE_URL,
            connect_args={"check_same_thread": False}
        )
        return sqlite_engine, "SQLITE_FALLBACK"

engine, ACTIVE_DB_TYPE = init_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def reconnect_db():
    global engine, SessionLocal, ACTIVE_DB_TYPE
    engine, ACTIVE_DB_TYPE = init_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return ACTIVE_DB_TYPE
