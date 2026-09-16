"""
Script facilitador para execução local do servidor FastAPI via Uvicorn.

Execução:
    python run.py
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("=" * 65)
    print(f"Iniciando {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    print(f"Servidor acessível em: http://{settings.APP_HOST}:{settings.APP_PORT}")
    print(f"Documentação Swagger UI: http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    print(f"Documentação ReDoc:      http://{settings.APP_HOST}:{settings.APP_PORT}/redoc")
    print("=" * 65)
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
