import os
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# =========================
# DATABASE URL
# =========================
RAW_URL = os.getenv("DATABASE_URL", "").strip()

if not RAW_URL:
    raise Exception("DATABASE_URL is not set in Vercel environment variables.")

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
# GET DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()