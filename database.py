import os
from urllib.parse import urlparse

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

# =========================
# DATABASE URL
# =========================
RAW_URL = os.getenv("POSTGRES_URL", "").strip()

if not RAW_URL:
    raise Exception("POSTGRES_URL is not set in Vercel environment variables.")

print("DATABASE_URL found.")

# =========================
# NORMALIZE POSTGRES URL
# =========================
if RAW_URL.startswith("postgres://"):
    DATABASE_URL = RAW_URL.replace(
        "postgres://",
        "postgresql+psycopg2://",
        1
    )
elif RAW_URL.startswith("postgresql://"):
    DATABASE_URL = RAW_URL.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1
    )
else:
    DATABASE_URL = RAW_URL

# =========================
# LOG SAFE HOST INFO
# =========================
parsed = urlparse(DATABASE_URL)

print(f"Using host: {parsed.hostname}")
print(f"Using port: {parsed.port}")

if "pooler.supabase.com" in DATABASE_URL:
    print("Using pooled Supabase connection.")
else:
    print("WARNING: NOT using pooled connection.")

# =========================
# ENGINE CONFIG
# =========================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connect_timeout": 10,
        "sslmode": "require"
    },
    echo=False
)

print("Database engine created successfully.")

# =========================
# SESSION LOCAL
# =========================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =========================
# BASE MODEL
# =========================
Base = declarative_base()

# =========================
# SAFE SCHEMA SYNC (no data loss)
# =========================
def sync_schema():
    """Auto-add missing columns to existing tables without dropping or losing data.

    Always adds columns as NULLable to avoid failures on tables with existing rows.
    ORM-level NOT NULL constraints remain enforced for new records via SQLAlchemy.
    """
    try:
        inspector = inspect(engine)
        for table_name, table in Base.metadata.tables.items():
            existing_columns = {c["name"] for c in inspector.get_columns(table_name)}
            model_columns = {c.name for c in table.columns}
            missing = model_columns - existing_columns
            if not missing:
                continue
            logger.info("Table '%s' — adding columns: %s", table_name, sorted(missing))
            for col_name in sorted(missing):
                col = table.columns[col_name]
                col_type = col.type.compile(engine.dialect)
                parts = [f'ALTER TABLE "{table_name}" ADD COLUMN "{col_name}" {col_type}']
                parts.append("NULL")
                if col.server_default and col.server_default.arg is not None:
                    parts.append(f"DEFAULT {col.server_default.arg.text}")
                sql = text(" ".join(parts))
                with engine.connect() as conn:
                    conn.execute(sql)
                    conn.commit()
                logger.info("  + %s", col_name)
        logger.info("Schema sync completed.")
    except Exception as e:
        logger.warning("Schema sync issue (non-fatal): %s", e)


# =========================
# GET DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()