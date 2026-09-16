"""
Schemas Pydantic para validação de dados de entrada (DTOs)
e serialização de respostas JSON na API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# =====================================================================
# Schemas para Categoria
# =====================================================================

class CategoriaBase(BaseModel):
    nome: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome único da categoria",
        examples=["Informática"]
    )
    descricao: Optional[str] = Field(
        None,
        max_length=255,
        description="Descrição detalhada do propósito da categoria",
        examples=["Equipamentos, periféricos e acessórios de informática"]
    )

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int = Field(..., description="Identificador único da categoria", examples=[1])
    criada_em: datetime = Field(..., description="Data e hora de criação no formato ISO 8601")

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# Schemas para Produto
# =====================================================================

class ProdutoBase(BaseModel):
    nome: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Nome descritivo do produto",
        examples=["Mouse Sem Fio Ergonômico"]
    )
    descricao: Optional[str] = Field(
        None,
        max_length=500,
        description="Descrição detalhada das características do produto",
        examples=["Mouse óptico sem fio recarregável, 1600 DPI, conexão 2.4GHz e Bluetooth."]
    )
    preco: float = Field(
        ...,
        gt=0,
        description="Preço unitário em Reais (deve ser estritamente positivo)",
        examples=[129.90]
    )
    estoque: int = Field(
        0,
        ge=0,
        description="Quantidade disponível em estoque (deve ser maior ou igual a zero)",
        examples=[45]
    )
    codigo_sku: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Código SKU único para controle de estoque",
        examples=["INF-MOU-001"]
    )
    categoria_id: int = Field(
        ...,
        gt=0,
        description="ID da categoria existente à qual o produto pertence",
        examples=[1]
    )
    ativo: bool = Field(
        True,
        description="Flag indicando se o produto está ativo no catálogo",
        examples=[True]
    )

class ProdutoCreate(ProdutoBase):
    """Schema utilizado para criar um novo produto (POST)."""
    pass

class ProdutoUpdate(ProdutoBase):
    """
    Schema utilizado para substituição integral do recurso (PUT).
    Todos os campos obrigatórios do recurso devem ser fornecidos.
    """
    pass

class ProdutoPatch(BaseModel):
    """
    Schema utilizado para modificação parcial do recurso (PATCH).
    Todos os campos são opcionais, atualizando apenas os atributos enviados.
    """
    nome: Optional[str] = Field(None, min_length=2, max_length=150, examples=["Mouse Sem Fio RGB"])
    descricao: Optional[str] = Field(None, max_length=500, examples=["Nova descrição com iluminação RGB"])
    preco: Optional[float] = Field(None, gt=0, examples=[149.90])
    estoque: Optional[int] = Field(None, ge=0, examples=[30])
    codigo_sku: Optional[str] = Field(None, min_length=3, max_length=50, examples=["INF-MOU-001-B"])
    categoria_id: Optional[int] = Field(None, gt=0, examples=[1])
    ativo: Optional[bool] = Field(None, examples=[True])

class ProdutoResponse(ProdutoBase):
    """Schema para serialização do recurso Produto nas respostas da API."""
    id: int = Field(..., description="Identificador numérico único do produto", examples=[1])
    criado_em: datetime = Field(..., description="Data e hora de cadastro")
    atualizado_em: datetime = Field(..., description="Data e hora da última alteração")
    categoria: Optional[CategoriaResponse] = Field(None, description="Dados da categoria associada")

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# Schemas de Respostas de Erro e Informações
# =====================================================================

class MensagemSucesso(BaseModel):
    mensagem: str = Field(..., examples=["Operação realizada com sucesso."])

class MensagemErro(BaseModel):
    detalhe: str = Field(..., examples=["Recurso não encontrado com o ID especificado."])
