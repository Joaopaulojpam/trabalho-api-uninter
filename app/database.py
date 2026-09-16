"""
Configuração da conexão com o banco de dados e gerenciamento de sessões com SQLAlchemy.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Para SQLite, 'check_same_thread=False' permite o compartilhamento seguro entre threads do FastAPI
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Criação da engine de conexão
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# Fábrica de sessões do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base declarativa para os modelos ORM
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Injetor de dependência (Dependency Injection) do FastAPI para fornecer
    uma sessão de banco de dados por requisição e fechá-la automaticamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
