"""
Ponto de entrada principal da aplicação FastAPI.
Configura middlewares (CORS), documentação interativa OpenAPI/Swagger,
registro de rotas e criação automática das tabelas no banco de dados.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import produtos, categorias

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida da aplicação.
    Garante a criação das tabelas no banco de dados SQLite na inicialização.
    """
    Base.metadata.create_all(bind=engine)
    yield

# Inicialização da aplicação FastAPI com metadados acadêmicos
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Produtos",
            "description": "Operações CRUD sobre o catálogo de produtos (recurso principal)."
        },
        {
            "name": "Categorias",
            "description": "Gestão de categorias e organização de itens do catálogo."
        },
        {
            "name": "Sistema",
            "description": "Rotas informativas e de verificação de integridade da API."
        }
    ]
)

# =====================================================================
# Configuração de CORS (Cross-Origin Resource Sharing)
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# =====================================================================
# Inclusão dos Roteadores de Recursos
# =====================================================================
app.include_router(produtos.router)
app.include_router(categorias.router)


# =====================================================================
# Rotas Informativas do Sistema
# =====================================================================
@app.get(
    "/",
    tags=["Sistema"],
    summary="Informações gerais e status da API",
    status_code=status.HTTP_200_OK
)
def root():
    return {
        "projeto": settings.PROJECT_NAME,
        "versao": settings.PROJECT_VERSION,
        "status": "online",
        "documentacao_swagger": "/docs",
        "documentacao_redoc": "/redoc",
        "disciplina": "Arquitetura e Desenvolvimento de APIs",
        "instituicao": "Centro Universitário Internacional UNINTER",
        "autenticacao": {
            "tipo": "API Key / Token Bearer",
            "cabecalhos_aceitos": ["X-API-Key", "Authorization: Bearer <chave>"],
            "chave_padrao_desenvolvimento": settings.API_KEY
        }
    }


@app.get(
    "/health",
    tags=["Sistema"],
    summary="Health check da API",
    status_code=status.HTTP_200_OK
)
def health_check():
    return {
        "status": "healthy",
        "banco_dados": "conectado",
        "modo_debug": settings.DEBUG
    }
