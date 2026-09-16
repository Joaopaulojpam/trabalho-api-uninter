"""
Endpoints para o recurso Categoria (/api/v1/categorias).
Demonstra a persistência e gerenciamento de relacionamentos 1:N no catálogo.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Categoria
from app.schemas import CategoriaCreate, CategoriaResponse
from app.security import verificar_autenticacao

router = APIRouter(prefix="/api/v1/categorias", tags=["Categorias"])

@router.get(
    "",
    response_model=List[CategoriaResponse],
    summary="Listar todas as categorias",
    description="Retorna a lista completa de categorias cadastradas no catálogo."
)
def listar_categorias(
    skip: int = Query(0, ge=0, description="Registros a ignorar para paginação"),
    limit: int = Query(50, ge=1, le=100, description="Quantidade máxima de registros"),
    db: Session = Depends(get_db)
):
    return db.query(Categoria).offset(skip).limit(limit).all()


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Buscar categoria por ID",
    description="Consulta os detalhes de uma categoria específica pelo seu identificador."
)
def obter_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com ID {categoria_id} não foi encontrada."
        )
    return categoria


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova categoria",
    description="Cadastra uma nova categoria no sistema. Requer autenticação (X-API-Key)."
)
def criar_categoria(
    categoria_in: CategoriaCreate,
    db: Session = Depends(get_db),
    _token: str = Depends(verificar_autenticacao)
):
    # Verifica duplicidade pelo nome
    existente = db.query(Categoria).filter(Categoria.nome.ilike(categoria_in.nome.strip())).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma categoria cadastrada com o nome '{categoria_in.nome}'."
        )

    nova_categoria = Categoria(
        nome=categoria_in.nome.strip(),
        descricao=categoria_in.descricao.strip() if categoria_in.descricao else None
    )
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    return nova_categoria


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir categoria por ID",
    description="Remove uma categoria existente e seus produtos vinculados em cascata. Requer autenticação."
)
def excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    _token: str = Depends(verificar_autenticacao)
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com ID {categoria_id} não encontrada para exclusão."
        )
    db.delete(categoria)
    db.commit()
    return None
