# app/core/db.py

from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./MyFitnessRank.db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    return Session(engine)

def init_db():
    SQLModel.metadata.create_all(engine)
