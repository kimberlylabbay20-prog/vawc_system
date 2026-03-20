from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace with your actual PostgreSQL credentials
DATABASE_URL = "postgresql://vawc_db_user:zHFBz1w5mhkXbkJdRLAW2QQvjq2Jt9wF@dpg-d6uct1vdiees73dfdmsg-a.singapore-postgres.render.com/vawc_db"

engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()