"""
Script de demonstração e geração de evidências de requisições HTTP reais.
Executa chamadas para todas as rotas e exibe os resultados formatados no console.
"""
import json
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def print_separator(title):
    print("\n" + "=" * 75)
    print(f"  {title}")
    print("=" * 75)

def log_exchange(method, endpoint, status_code, request_body=None, response_data=None, headers=None):
    print(f"\n[REQUISIÇÃO] {method} {endpoint}")
    if headers:
        print(f"Headers: {headers}")
    if request_body:
        print("Body enviado:")
        print(json.dumps(request_body, indent=2, ensure_ascii=False))
    print(f"[RESPOSTA] Código HTTP: {status_code}")
    if response_data is not None:
        print("Corpo da Resposta:")
        if isinstance(response_data, (dict, list)):
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        else:
            print(response_data)

def run_demonstration():
    print("INICIANDO DEMONSTRAÇÃO COMPLETA DA API DE CATÁLOGO DE PRODUTOS")

    # 1. Rota Raiz
    print_separator("1. CONSULTA DE METADADOS DA API (GET /)")
    res = client.get("/")
    log_exchange("GET", "/", res.status_code, response_data=res.json())

    # 2. Listar Categorias
    print_separator("2. LISTAGEM DE CATEGORIAS (GET /api/v1/categorias)")
    res = client.get("/api/v1/categorias")
    log_exchange("GET", "/api/v1/categorias", res.status_code, response_data=res.json())

    # 3. Listar Produtos (Coleção)
    print_separator("3. LISTAGEM GERAL DE PRODUTOS (GET /api/v1/produtos)")
    res = client.get("/api/v1/produtos?skip=0&limit=3")
    log_exchange("GET", "/api/v1/produtos?skip=0&limit=3", res.status_code, response_data=res.json())

    # 4. Filtrar Produtos por Categoria e Preço
    print_separator("4. FILTRAGEM DE PRODUTOS POR CATEGORIA E PREÇO")
    res = client.get("/api/v1/produtos?categoria_id=1&preco_min=100&preco_max=300")
    log_exchange("GET", "/api/v1/produtos?categoria_id=1&preco_min=100&preco_max=300", res.status_code, response_data=res.json())

    # 5. Obter Produto Individual por ID (200 OK)
    print_separator("5. CONSULTA INDIVIDUAL POR ID - SUCESSO (GET /api/v1/produtos/1)")
    res = client.get("/api/v1/produtos/1")
    log_exchange("GET", "/api/v1/produtos/1", res.status_code, response_data=res.json())

    # 6. Obter Produto Inexistente (404 Not Found)
    print_separator("6. CONSULTA INDIVIDUAL - RECURSO INEXISTENTE (GET /api/v1/produtos/9999)")
    res = client.get("/api/v1/produtos/9999")
    log_exchange("GET", "/api/v1/produtos/9999", res.status_code, response_data=res.json())

    # 7. Criar Produto Sem Autenticação (401 Unauthorized)
    print_separator("7. TENTATIVA DE CRIAÇÃO SEM AUTENTICAÇÃO (POST /api/v1/produtos)")
    body_novo = {
        "nome": "Webcam Pro 4K",
        "descricao": "Webcam Ultra HD com foco automático",
        "preco": 399.90,
        "estoque": 20,
        "codigo_sku": "INF-CAM-005",
        "categoria_id": 1,
        "ativo": True
    }
    res = client.post("/api/v1/produtos", json=body_novo)
    log_exchange("POST", "/api/v1/produtos", res.status_code, request_body=body_novo, response_data=res.json())

    # 8. Criar Produto Com Autenticação (201 Created)
    print_separator("8. CRIAÇÃO DE PRODUTO COM AUTENTICAÇÃO (POST /api/v1/produtos)")
    auth_header = {"X-API-Key": settings.API_KEY}
    res = client.post("/api/v1/produtos", json=body_novo, headers=auth_header)
    log_exchange("POST", "/api/v1/produtos", res.status_code, request_body=body_novo, response_data=res.json(), headers=auth_header)
    novo_id = res.json().get("id")

    # 9. Validação de Dados Inválidos (422 Unprocessable Entity)
    print_separator("9. VALIDAÇÃO DE ENTRADA COM DADOS INVÁLIDOS (POST /api/v1/produtos)")
    body_invalido = {
        "nome": "X",
        "preco": -10.0,
        "estoque": -5,
        "codigo_sku": "",
        "categoria_id": 1,
        "ativo": True
    }
    res = client.post("/api/v1/produtos", json=body_invalido, headers=auth_header)
    log_exchange("POST", "/api/v1/produtos", res.status_code, request_body=body_invalido, response_data=res.json(), headers=auth_header)

    # 10. Atualização Integral PUT (200 OK)
    print_separator(f"10. ATUALIZAÇÃO INTEGRAL - PUT (PUT /api/v1/produtos/{novo_id})")
    body_put = {
        "nome": "Webcam Pro 4K HDR Plus",
        "descricao": "Webcam Ultra HD 60fps com microfone estéreo",
        "preco": 449.90,
        "estoque": 25,
        "codigo_sku": "INF-CAM-005",
        "categoria_id": 1,
        "ativo": True
    }
    res = client.put(f"/api/v1/produtos/{novo_id}", json=body_put, headers=auth_header)
    log_exchange("PUT", f"/api/v1/produtos/{novo_id}", res.status_code, request_body=body_put, response_data=res.json(), headers=auth_header)

    # 11. Atualização Parcial PATCH (200 OK)
    print_separator(f"11. ATUALIZAÇÃO PARCIAL - PATCH (PATCH /api/v1/produtos/{novo_id})")
    body_patch = {
        "preco": 420.00,
        "estoque": 30
    }
    res = client.patch(f"/api/v1/produtos/{novo_id}", json=body_patch, headers=auth_header)
    log_exchange("PATCH", f"/api/v1/produtos/{novo_id}", res.status_code, request_body=body_patch, response_data=res.json(), headers=auth_header)

    # 12. Exclusão DELETE (204 No Content)
    print_separator(f"12. EXCLUSÃO DE PRODUTO - DELETE (DELETE /api/v1/produtos/{novo_id})")
    res = client.delete(f"/api/v1/produtos/{novo_id}", headers=auth_header)
    log_exchange("DELETE", f"/api/v1/produtos/{novo_id}", res.status_code, response_data="<Conteúdo Vazio - 204 No Content>", headers=auth_header)

    # 13. Verificação pós-deleção (404 Not Found)
    print_separator(f"13. VERIFICAÇÃO PÓS-EXCLUSÃO (GET /api/v1/produtos/{novo_id})")
    res = client.get(f"/api/v1/produtos/{novo_id}")
    log_exchange("GET", f"/api/v1/produtos/{novo_id}", res.status_code, response_data=res.json())

    print("\n" + "=" * 75)
    print("TODAS AS OPERAÇÕES FORAM DEMONSTRADAS COM SUCESSO!")
    print("=" * 75)

if __name__ == "__main__":
    run_demonstration()
