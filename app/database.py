import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

#load environment variables from .env
load_dotenv()

# read DB URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# set up the engine (sqlLite for now)
engine = create_engine(DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}                   
)

# create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# shared base class for all models
Base = declarative_base()