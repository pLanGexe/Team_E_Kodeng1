from sqlalchemy import create_engine, text
import os

DB_USER = os.getenv("POSTGRES_USER", "app_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "app_password")
DB_NAME = os.getenv("POSTGRES_DB", "app_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, future=True)

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS counters (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                value INTEGER NOT NULL DEFAULT 0
            )
        """))

def increment_and_get(name="global"):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO counters (name, value)
            VALUES (:name, 0)
            ON CONFLICT (name) DO NOTHING
        """), {"name": name})
        conn.execute(text("""
            UPDATE counters SET value = value + 1 WHERE name = :name
        """), {"name": name})
        row = conn.execute(text("""
            SELECT value FROM counters WHERE name = :name
        """), {"name": name}).one()
        return row
