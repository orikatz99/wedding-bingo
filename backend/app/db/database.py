from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.config import DATABASE_URL
from app.db.models import Base

# Database setup
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
#autocommit=False:don't automatically commit transactions, you have to call commit() explicitly.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)