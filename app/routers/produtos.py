"""
Endpoints CRUD completos para o recurso principal Produto (/api/v1/produtos).
Implementa GET (listagem com filtros e paginação), GET (individual),
POST (criação protegida), PUT (atualização total), PATCH (atualização parcial)
e DELETE (exclusão com status 204).
"""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import Produto, Categoria
from app.schemas import (
    ProdutoCreate,
    ProdutoUpdate,
    ProdutoPatch,
    ProdutoResponse,
    MensagemErro
)
from app.security import verificar_autenticacao

router = APIRouter(prefix="/api/v1/produtos", tags=["Produtos"])

def _utc_now():
    return datetime.now(timezone.utc)


@router.get(
    "",
    response_model=List[ProdutoResponse],
    summary="Listar produtos com filtros e paginação",
    description=(
        "Retorna uma coleção de produtos cadastrados no catálogo. "
        "Suporta paginação (skip/limit), filtro por categoria, busca textual por termo "
        "e intervalo de valores (preco_min e preco_max)."
    )
)
def listar_produtos(
    skip: int = Query(0, ge=0, description="Número de registros ignorados para paginação"),
    limit: int = Query(20, ge=1, le=100, description="Limite de registros retornados"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por ID da categoria"),
    busca: Optional[str] = Query(None, min_length=1, description="Busca textual por nome ou descrição"),
    preco_min: Optional[float] = Query(None, ge=0, description="Preço mínimo para filtragem"),
    preco_max: Optional[float] = Query(None, ge=0, description="Preço máximo para filtragem"),
    apenas_ativos: bool = Query(True, description="Se verdadeiro, retorna apenas produtos ativos no catálogo"),
    db: Session = Depends(get_db)
):
    query = db.query(Produto)

    if apenas_ativos:
        query = query.filter(Produto.ativo == True)

    if categoria_id is not None:
        query = query.filter(Produto.categoria_id == categoria_id)

    if preco_min is not None:
        query = query.filter(Produto.preco >= preco_min)

    if preco_max is not None:
        query = query.filter(Produto.preco <= preco_max)

    if busca:
        termo = f"%{busca.strip()}%"
        query = query.filter(
            or_(
                Produto.nome.ilike(termo),
                Produto.descricao.ilike(termo),
                Produto.codigo_sku.ilike(termo)
            )
        )

    produtos = query.order_by(Produto.id.asc()).offset(skip).limit(limit).all()
    return produtos


@router.get(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Consultar produto individual por ID",
    description="Recupera todos os detalhes de um produto específico através do seu identificador numérico único.",
    responses={
        404: {"model": MensagemErro, "description": "Produto não encontrado"}
    }
)
def obter_produto(
    produto_id: int = Path(..., gt=0, description="ID do produto a ser consultado"),
    db: Session = Depends(get_db)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não foi encontrado no catálogo."
        )
    return produto


@router.post(
    "",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo produto (Protegido)",
    description=(
        "Cadastra um novo produto no catálogo. "
        "Requer cabeçalho de autenticação X-API-Key ou Bearer Token. "
        "Valida existência da categoria e unicidade do código SKU."
    ),
    responses={
        401: {"model": MensagemErro, "description": "Credenciais de autenticação ausentes ou inválidas"},
        404: {"model": MensagemErro, "description": "Categoria associada não existe"},
        409: {"model": MensagemErro, "description": "Conflito: código SKU já cadastrado"},
        422: {"description": "Dados de entrada inválidos"}
    }
)
def criar_produto(
    produto_in: ProdutoCreate,
    db: Session = Depends(get_db),
    _token: str = Depends(verificar_autenticacao)
):
    # Valida se a categoria informada existe
    categoria = db.query(Categoria).filter(Categoria.id == produto_in.categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"A categoria com ID {produto_in.categoria_id} não existe. Cadastre-a antes de vincular produtos."
        )

    # Valida unicidade do código SKU
    sku_existente = db.query(Produto).filter(Produto.codigo_sku == produto_in.codigo_sku.strip()).first()
    if sku_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um produto cadastrado com o código SKU '{produto_in.codigo_sku}'."
        )

    novo_produto = Produto(
        nome=produto_in.nome.strip(),
        descricao=produto_in.descricao.strip() if produto_in.descricao else None,
        preco=produto_in.preco,
        estoque=produto_in.estoque,
        codigo_sku=produto_in.codigo_sku.strip().upper(),
        categoria_id=produto_in.categoria_id,
        ativo=produto_in.ativo
    )

    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


@router.put(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Atualizar produto integralmente - PUT (Protegido)",
    description=(
        "Substituição integral e idempotente de um produto existente. "
        "Todos os campos do recurso devem ser fornecidos. Requer autenticação."
    ),
    responses={
        401: {"model": MensagemErro, "description": "Não autorizado"},
        404: {"model": MensagemErro, "description": "Produto ou Categoria não encontrado"},
        409: {"model": MensagemErro, "description": "Conflito com SKU existente de outro produto"}
    }
)
def atualizar_produto_put(
    produto_id: int = Path(..., gt=0, description="ID do produto a ser atualizado"),
    produto_in: ProdutoUpdate = ...,
    db: Session = Depends(get_db),
    _token: str = Depends(verificar_autenticacao)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não foi encontrado para atualização."
        )

    # Valida existência da nova categoria informada
    categoria = db.query(Categoria).filter(Categoria.id == produto_in.categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"A categoria com ID {produto_in.categoria_id} não existe."
        )

    # Verifica se o SKU foi alterado e se conflita com outro produto diferente
    sku_formatado = produto_in.codigo_sku.strip().upper()
    sku_existente = db.query(Produto).filter(
        Produto.codigo_sku == sku_formatado,
        Produto.id != produto_id
    ).first()
    if sku_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"O código SKU '{sku_formatado}' já está em uso por outro produto (ID {sku_existente.id})."
        )

    # Substituição completa dos dados do recurso
    produto.nome = produto_in.nome.strip()
    produto.descricao = produto_in.descricao.strip() if produto_in.descricao else None
    produto.preco = produto_in.preco
    produto.estoque = produto_in.estoque
    produto.codigo_sku = sku_formatado
    produto.categoria_id = produto_in.categoria_id
    produto.ativo = produto_in.ativo
    produto.atualizado_em = _utc_now()

    db.commit()
    db.refresh(produto)
    return produto


@router.patch(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Atualizar produto parcialmente - PATCH (Protegido)",
    description=(
        "Atualização parcial de um produto existente. "
        "Apenas os campos enviados no corpo JSON serão alterados. Requer autenticação."
    ),
    responses={
        401: {"model": MensagemErro, "description": "Não autorizado"},
        404: {"model": MensagemErro, "description": "Produto ou Categoria não encontrado"},
        409: {"model": MensagemErro, "description": "Conflito com SKU existente de outro produto"}
    }
)
def atualizar_produto_patch(
    produto_id: int = Path(..., gt=0, description="ID do produto a ser alterado"),
    produto_in: ProdutoPatch = ...,
    db: Session = Depends(get_db),
    _token: str = Depends(verificar_autenticacao)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não foi encontrado para alteração."
        )

    dados_atualizacao = produto_in.model_dump(exclude_unset=True)

    if not dados_atualizacao:
        return produto

    # Se categoria_id for alterada, valida existência
    if "categoria_id" in dados_atualizacao:
        cat_id = dados_atualizacao["categoria_id"]
        categoria = db.query(Categoria).filter(Categoria.id == cat_id).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"A categoria com ID {cat_id} não existe."
            )

    # Se codigo_sku for alterado, valida unicidade
    if "codigo_sku" in dados_atualizacao:
        sku_formatado = dados_atualizacao["codigo_sku"].strip().upper()
        sku_existente = db.query(Produto).filter(
            Produto.codigo_sku == sku_formatado,
            Produto.id != produto_id
        ).first()
        if sku_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"O código SKU '{sku_formatado}' já está em uso por outro produto."
            )
        dados_atualizacao["codigo_sku"] = sku_formatado

    # Aplica alterações nos campos fornecidos
    for campo, valor in dados_atualizacao.items():
        if isinstance(valor, str) and campo in ("nome", "descricao"):
            valor = valor.strip()
        setattr(produto, campo, valor)

    produto.atualizado_em = _utc_now()
    db.commit()
    db.refresh(produto)
    return produto


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir produto - DELETE (Protegido)",
    description=(
        "Remove permanentemente um produto do catálogo pelo seu identificador. "
        "Retorna status HTTP 204 No Content em caso de sucesso. Requer autenticação."
    ),
    responses={
        204: {"description": "Produto removido com sucesso (sem conteúdo no corpo)"},
        401: {"model": MensagemErro, "description": "Não autorizado"},
        404: {"model": MensagemErro, "description": "Produto não encontrado"}
    }
)
def excluir_produto(
    produto_id: int = Path(..., gt=0, description="ID do produto a ser excluído"),
    db: Session = Depends(get_db),
    _token: str = Depends(verificar_autenticacao)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não foi encontrado para exclusão."
        )

    db.delete(produto)
    db.commit()
    return None
