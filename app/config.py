"""
Módulo de configurações centrais da aplicação.
Carrega variáveis do arquivo .env com fallbacks seguros.
"""
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

class Settings:
    PROJECT_NAME: str = "API de Catálogo de Produtos e Categorias"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = (
        "API RESTful desenvolvida para a Atividade Prática da disciplina "
        "Arquitetura e Desenvolvimento de APIs (UNINTER - 2026). "
        "Demonstra operações CRUD completas, mapeamento objeto-relacional (ORM), "
        "persistência em banco de dados, autenticação via API Key, tratamento de erros "
        "e padronização de códigos de resposta HTTP."
    )
    
    # Chave de segurança para endpoints protegidos
    API_KEY: str = os.getenv("API_KEY", "uninter_segredo_api_2026")
    
    # URL de conexão com o banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./catalogo.db")
    
    # Configuração de CORS (aceita lista separada por vírgula ou '*')
    CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS", "*")
    
    @property
    def cors_origins(self) -> list[str]:
        if self.CORS_ORIGINS_RAW.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

settings = Settings()
