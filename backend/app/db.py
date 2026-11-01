# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# load_dotenv()
# DATABASE_URL=os.getenv("DATABASE_URL","mysql+pymysql://root:change_me@localhost:3306/abandoned_cart_recovery")
# engine=create_engine(DATABASE_URL,pool_pre_ping=True,pool_recycle=3600)
# SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
# def get_db():
#     db=SessionLocal()
#     try: yield db
#     finally: db.close()



import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Locate the backend folder and load its .env file
BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:change_me@localhost:3306/abandoned_cart_recovery"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
