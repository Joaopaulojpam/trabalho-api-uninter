"""
Módulo de Segurança e Autenticação.
Implementa o controle de acesso baseado em API Key / Token Bearer.
Protege operações sensíveis de modificação e exclusão de dados (POST, PUT, PATCH, DELETE).
"""
from typing import Optional
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

# Definição dos esquemas de segurança para a documentação Swagger/OpenAPI
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False, description="Chave de autenticação via cabeçalho X-API-Key")
bearer_scheme = HTTPBearer(auto_error=False, description="Token Bearer no cabeçalho Authorization: Bearer <token>")

def verificar_autenticacao(
    api_key: Optional[str] = Security(api_key_header),
    bearer_token: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> str:
    """
    Valida a presença e exatidão da credencial enviada na requisição.
    Aceita tanto 'X-API-Key: <chave>' quanto 'Authorization: Bearer <chave>'.
    Retorna 401 Unauthorized se nenhuma credencial válida for encontrada.
    """
    token_fornecido = None
    
    if api_key:
        token_fornecido = api_key.strip()
    elif bearer_token and bearer_token.credentials:
        token_fornecido = bearer_token.credentials.strip()

    if not token_fornecido or token_fornecido != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso não autorizado: Chave de API ou Token Bearer inválido ou não fornecido.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    return token_fornecido
