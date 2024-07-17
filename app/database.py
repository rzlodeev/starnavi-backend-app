from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session

DATABASE_URL = 'sqlite:///./db/database.db'

engine = create_engine(DATABASE_URL)
metadata = MetaData()

Base = declarative_base(metadata=metadata)

# metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
