from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.config import settings

URL = settings.psycopg_GET_DB

engine = create_engine(URL, echo=True)
localSession = sessionmaker(engine)
