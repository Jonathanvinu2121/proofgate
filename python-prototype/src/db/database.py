"""
Database connection and session configuration for PostgreSQL + pgvector.
Provides graceful connection attempt and fallback flag if Postgres is unreachable.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rag_agent_db")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

Base = declarative_base()


def get_db_engine():
    """
    Attempts to create and connect to Postgres engine.
    Returns (engine, is_connected_bool).
    """
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 2})
        with engine.connect() as conn:
            pass
        return engine, True
    except Exception:
        return None, False


def get_session_local(engine):
    if engine is None:
        return None
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()
