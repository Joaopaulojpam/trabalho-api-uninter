"""
Suíte de Testes Automatizados da API de Catálogo de Produtos.
Utiliza pytest e FastAPI TestClient (baseado no HTTPX).
Cobre todos os endpoints, status HTTP (200, 201, 204, 400/422, 401, 404, 409),
filtros, paginação e fluxos de autenticação.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Categoria, Produto
from app.config import settings

# Banco de dados SQLite em memória isolado para os testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sobrescreve a dependência de banco de dados do FastAPI para usar o banco em memória
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

AUTH_HEADER = {"X-API-Key": settings.API_KEY}
BEARER_HEADER = {"Authorization": f"Bearer {settings.API_KEY}"}

@pytest.fixture(autouse=True)
def setup_banco():
    """Recria o esquema do banco antes de cada teste e insere dados base."""
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    db = TestingSessionLocal()
    # Cria categorias base
    cat1 = Categoria(id=1, nome="Informática", descricao="Equipamentos de TI")
    cat2 = Categoria(id=2, nome="Telefonia", descricao="Smartphones e acessórios")
    db.add_all([cat1, cat2])
    db.commit()

    # Cria produtos base
    prod1 = Produto(
        id=1,
        nome="Mouse Sem Fio",
        descricao="Mouse óptico 1600 DPI",
        preco=89.90,
        estoque=30,
        codigo_sku="TEST-MOU-01",
        categoria_id=1,
        ativo=True
    )
    prod2 = Produto(
        id=2,
        nome="Teclado Mecânico",
        descricao="Teclado RGB switch blue",
        preco=250.00,
        estoque=15,
        codigo_sku="TEST-TEC-02",
        categoria_id=1,
        ativo=True
    )
    prod3 = Produto(
        id=3,
        nome="Cabo USB-C",
        descricao="Cabo reforçado 2 metros",
        preco=35.00,
        estoque=50,
        codigo_sku="TEST-CAB-03",
        categoria_id=2,
        ativo=True
    )
    db.add_all([prod1, prod2, prod3])
    db.commit()
    db.close()


# =====================================================================
# 1. Testes de Sistema e Rotas Base
# =====================================================================

def test_rota_raiz():
    response = client.get("/")
    assert response.status_code == 200
    dados = response.json()
    assert dados["status"] == "online"
    assert "documentacao_swagger" in dados

def test_rota_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# =====================================================================
# 2. Testes de Categorias
# =====================================================================

def test_listar_categorias():
    response = client.get("/api/v1/categorias")
    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 2
    assert dados[0]["nome"] == "Informática"

def test_obter_categoria_por_id():
    response = client.get("/api/v1/categorias/1")
    assert response.status_code == 200
    assert response.json()["nome"] == "Informática"

def test_obter_categoria_inexistente():
    response = client.get("/api/v1/categorias/999")
    assert response.status_code == 404

def test_criar_categoria_sem_auth():
    response = client.post("/api/v1/categorias", json={"nome": "Livros"})
    assert response.status_code == 401

def test_criar_categoria_com_auth():
    response = client.post(
        "/api/v1/categorias",
        json={"nome": "Livros", "descricao": "Livros e manuais técnicos"},
        headers=AUTH_HEADER
    )
    assert response.status_code == 201
    dados = response.json()
    assert dados["nome"] == "Livros"
    assert "id" in dados

def test_criar_categoria_nome_duplicado():
    response = client.post(
        "/api/v1/categorias",
        json={"nome": "Informática"},
        headers=AUTH_HEADER
    )
    assert response.status_code == 409


# =====================================================================
# 3. Testes do Recurso Principal: Produto (CRUD Completo)
# =====================================================================

def test_listar_produtos():
    response = client.get("/api/v1/produtos")
    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 3

def test_filtrar_produtos_por_categoria():
    response = client.get("/api/v1/produtos?categoria_id=2")
    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 1
    assert dados[0]["codigo_sku"] == "TEST-CAB-03"

def test_filtrar_produtos_por_faixa_preco():
    response = client.get("/api/v1/produtos?preco_min=50.0&preco_max=100.0")
    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 1
    assert dados[0]["nome"] == "Mouse Sem Fio"

def test_buscar_produtos_por_termo():
    response = client.get("/api/v1/produtos?busca=mecânico")
    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 1
    assert "Teclado Mecânico" in dados[0]["nome"]

def test_obter_produto_por_id():
    response = client.get("/api/v1/produtos/1")
    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == 1
    assert dados["nome"] == "Mouse Sem Fio"
    assert dados["categoria"]["nome"] == "Informática"

def test_obter_produto_inexistente_retorna_404():
    response = client.get("/api/v1/produtos/9999")
    assert response.status_code == 404
    assert "não foi encontrado" in response.json()["detail"]

def test_criar_produto_sem_autenticacao_retorna_401():
    novo_produto = {
        "nome": "Webcam Full HD",
        "descricao": "Webcam 1080p com microfone integrado",
        "preco": 199.90,
        "estoque": 25,
        "codigo_sku": "TEST-WEB-04",
        "categoria_id": 1,
        "ativo": True
    }
    response = client.post("/api/v1/produtos", json=novo_produto)
    assert response.status_code == 401

def test_criar_produto_com_autenticacao_retorna_201():
    novo_produto = {
        "nome": "Webcam Full HD",
        "descricao": "Webcam 1080p com microfone integrado",
        "preco": 199.90,
        "estoque": 25,
        "codigo_sku": "TEST-WEB-04",
        "categoria_id": 1,
        "ativo": True
    }
    response = client.post("/api/v1/produtos", json=novo_produto, headers=AUTH_HEADER)
    assert response.status_code == 201
    dados = response.json()
    assert dados["nome"] == "Webcam Full HD"
    assert dados["codigo_sku"] == "TEST-WEB-04"
    assert dados["id"] is not None

def test_criar_produto_com_bearer_token_retorna_201():
    novo_produto = {
        "nome": "Monitor LED 24",
        "descricao": "Monitor 75Hz HDMI",
        "preco": 650.00,
        "estoque": 10,
        "codigo_sku": "TEST-MON-05",
        "categoria_id": 1,
        "ativo": True
    }
    response = client.post("/api/v1/produtos", json=novo_produto, headers=BEARER_HEADER)
    assert response.status_code == 201
    assert response.json()["codigo_sku"] == "TEST-MON-05"

def test_criar_produto_com_preco_invalido_retorna_422():
    produto_invalido = {
        "nome": "Produto Teste Preço Negativo",
        "preco": -15.00,  # Inválido: gt=0
        "estoque": 5,
        "codigo_sku": "TEST-NEG-01",
        "categoria_id": 1,
        "ativo": True
    }
    response = client.post("/api/v1/produtos", json=produto_invalido, headers=AUTH_HEADER)
    assert response.status_code == 422

def test_criar_produto_categoria_inexistente_retorna_404():
    produto_cat_invalida = {
        "nome": "Produto Categoria Fantasma",
        "preco": 50.00,
        "estoque": 5,
        "codigo_sku": "TEST-FAN-01",
        "categoria_id": 9999,
        "ativo": True
    }
    response = client.post("/api/v1/produtos", json=produto_cat_invalida, headers=AUTH_HEADER)
    assert response.status_code == 404
    assert "não existe" in response.json()["detail"]

def test_criar_produto_sku_duplicado_retorna_409():
    produto_duplicado = {
        "nome": "Outro Mouse",
        "preco": 80.00,
        "estoque": 10,
        "codigo_sku": "TEST-MOU-01",  # Já existe no setup_banco
        "categoria_id": 1,
        "ativo": True
    }
    response = client.post("/api/v1/produtos", json=produto_duplicado, headers=AUTH_HEADER)
    assert response.status_code == 409
    assert "Já existe um produto" in response.json()["detail"]


# =====================================================================
# 4. Testes de Atualização: PUT (Integral) e PATCH (Parcial)
# =====================================================================

def test_atualizar_produto_put_sucesso():
    dados_completos = {
        "nome": "Mouse Sem Fio PRO Max",
        "descricao": "Mouse óptico atualizado com bateria de lítio",
        "preco": 119.90,
        "estoque": 40,
        "codigo_sku": "TEST-MOU-01",
        "categoria_id": 1,
        "ativo": True
    }
    response = client.put("/api/v1/produtos/1", json=dados_completos, headers=AUTH_HEADER)
    assert response.status_code == 200
    dados = response.json()
    assert dados["nome"] == "Mouse Sem Fio PRO Max"
    assert dados["preco"] == 119.90
    assert dados["estoque"] == 40

def test_atualizar_produto_put_inexistente_retorna_404():
    dados_completos = {
        "nome": "Inexistente",
        "preco": 100.0,
        "estoque": 1,
        "codigo_sku": "SKU-9999",
        "categoria_id": 1,
        "ativo": True
    }
    response = client.put("/api/v1/produtos/9999", json=dados_completos, headers=AUTH_HEADER)
    assert response.status_code == 404

def test_atualizar_produto_patch_parcial_sucesso():
    # Altera apenas o preço e o estoque sem reenviar os demais campos
    dados_parciais = {
        "preco": 99.90,
        "estoque": 100
    }
    response = client.patch("/api/v1/produtos/1", json=dados_parciais, headers=AUTH_HEADER)
    assert response.status_code == 200
    dados = response.json()
    assert dados["preco"] == 99.90
    assert dados["estoque"] == 100
    # O nome original deve ter sido preservado
    assert dados["nome"] == "Mouse Sem Fio"

def test_atualizar_produto_patch_sem_autenticacao_retorna_401():
    response = client.patch("/api/v1/produtos/1", json={"preco": 50.0})
    assert response.status_code == 401


# =====================================================================
# 5. Testes de Exclusão: DELETE
# =====================================================================

def test_excluir_produto_sem_autenticacao_retorna_401():
    response = client.delete("/api/v1/produtos/1")
    assert response.status_code == 401

def test_excluir_produto_sucesso_retorna_204():
    response = client.delete("/api/v1/produtos/1", headers=AUTH_HEADER)
    assert response.status_code == 204

    # Confirma que o recurso foi realmente excluído do banco
    consulta = client.get("/api/v1/produtos/1")
    assert consulta.status_code == 404

def test_excluir_produto_inexistente_retorna_404():
    response = client.delete("/api/v1/produtos/9999", headers=AUTH_HEADER)
    assert response.status_code == 404
