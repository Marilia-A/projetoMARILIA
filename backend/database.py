import os
import re

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./marilia.db").strip()
achado = re.search(r"(?:postgres(?:ql)?(?:\+\w+)?|sqlite)://[^\s'\"]+", DATABASE_URL)
if achado:
    DATABASE_URL = achado.group(0)
DATABASE_URL = re.sub(r"^postgres(?:ql)?(?:\+\w+)?://", "postgresql+psycopg://", DATABASE_URL)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)


def criar_tabelas():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session