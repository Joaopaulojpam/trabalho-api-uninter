"""
Modelos ORM (Mapeamento Objeto-Relacional) utilizando SQLAlchemy.
Define as tabelas, tipos de dados, restrições e relacionamentos entre entidades.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Categoria(Base):
    """
    Entidade Categoria: representa os grupos/departamentos aos quais os produtos pertencem.
    Relacionamento: 1 Categoria para N Produtos (1:N).
    """
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    descricao = Column(String(255), nullable=True)
    criada_em = Column(DateTime, default=utc_now, nullable=False)

    # Relacionamento 1:N com Produto
    produtos = relationship("Produto", back_populates="categoria", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Categoria(id={self.id}, nome='{self.nome}')>"


class Produto(Base):
    """
    Entidade Produto: recurso principal da API de catálogo.
    Armazena informações de identificação, precificação, inventário e categoria associada.
    """
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(150), nullable=False, index=True)
    descricao = Column(String(500), nullable=True)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0, nullable=False)
    codigo_sku = Column(String(50), unique=True, index=True, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=utc_now, nullable=False)
    atualizado_em = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relacionamento N:1 com Categoria
    categoria = relationship("Categoria", back_populates="produtos")

    def __repr__(self):
        return f"<Produto(id={self.id}, nome='{self.nome}', sku='{self.codigo_sku}')>"
