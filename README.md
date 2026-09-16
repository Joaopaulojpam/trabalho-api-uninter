# API de Catálogo de Produtos e Categorias

> **Atividade Prática — Disciplina: Arquitetura e Desenvolvimento de APIs**  
> **Instituição:** Centro Universitário Internacional UNINTER  
> **Ano:** 2026  
> **Docentes:** Prof. Pedro Henrique Flores e Prof. Osmar Dias Jr.

---

## 1. Descrição da API e do Problema Resolvido

No comércio eletrônico e na gestão corporativa moderna, a centralização e a padronização do inventário de mercadorias são cruciais para a consistência das operações. Esta aplicação consiste em uma **API Web RESTful** projetada para gerenciar um **Catálogo de Produtos e Categorias**.

A API resolve a necessidade de manipulação remota e segura de itens por múltiplos clientes (aplicações web, aplicativos móveis e sistemas de frente de caixa), permitindo:
- Consulta estruturada com filtros avançados (busca textual, faixa de preço, categoria e status);
- Cadastro, atualização integral (`PUT`) e atualização parcial (`PATCH`) de itens;
- Exclusão controlada com integridade referencial;
- Proteção de rotas sensíveis via autenticação por chave de API ou Token Bearer;
- Persistência permanente em banco de dados relacional via ORM;
- Suporte a CORS para integração transparente com clientes web externos.

---

## 2. Tecnologias Utilizadas

| Tecnologia | Versão Mínima | Função na Arquitetura |
| :--- | :--- | :--- |
| **Python** | 3.10+ (Homologado em 3.14) | Linguagem de programação principal |
| **FastAPI** | 0.110+ | Framework web assíncrono para construção de APIs RESTful |
| **Uvicorn** | 0.28+ | Servidor ASGI de alta performance |
| **SQLAlchemy** | 2.0+ | Ferramenta de Mapeamento Objeto-Relacional (ORM) |
| **SQLite** | 3.x (Nativo) | Sistema Gerenciador de Banco de Dados Relacional persistente |
| **Pydantic** | 2.0+ | Validação estrita de esquemas e serialização de dados (DTOs) |
| **Pytest & HTTPX** | 8.0+ / 0.27+ | Framework de testes automatizados e cliente HTTP de teste |
| **Swagger UI / OpenAPI**| 3.1 (Integrado) | Documentação interativa nativa nos endpoints `/docs` e `/redoc` |

---

## 3. Pré-requisitos

- **Python 3.10** ou superior instalado no sistema operacional (Windows, Linux ou macOS).
- Gerenciador de pacotes **pip** configurado no PATH do sistema.
- Acesso à internet para download inicial das bibliotecas listadas no `requirements.txt`.

---

## 4. Instalação das Dependências

Abra o terminal na pasta raiz do projeto e execute:

```bash
# Opcional (Recomendado): Criar e ativar um ambiente virtual
python -m venv venv

# No Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# No Windows (Prompt de Comando CMD):
.\venv\Scripts\activate.bat
# No Linux/macOS:
source venv/bin/activate

# Instalar dependências do projeto
pip install -r requirements.txt
```

---

## 5. Configuração de Banco de Dados e Variáveis de Ambiente

A aplicação utiliza um arquivo `.env` para carregar as configurações do sistema. Para iniciar:

1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   # Windows (PowerShell ou CMD):
   copy .env.example .env

   # Linux / macOS:
   cp .env.example .env
   ```

2. O arquivo `.env` já vem pré-configurado para execução imediata em ambiente de desenvolvimento local:
   ```ini
   API_KEY=uninter_segredo_api_2026
   DATABASE_URL=sqlite:///./catalogo.db
   CORS_ORIGINS=*
   APP_HOST=127.0.0.1
   APP_PORT=8000
   DEBUG=True
   ```
   > **Nota de Segurança:** Em ambientes de produção reais, a variável `API_KEY` deve conter uma chave criptográfica forte e o arquivo `.env` nunca deve ser versionado no repositório público (já incluído no `.gitignore`).

---

## 6. Inicialização do Banco de Dados (Seed)

Para criar as tabelas e carregar um conjunto inicial de categorias e produtos para avaliação imediata, execute:

```bash
python seed.py
```

*Saída esperada:*
```text
=================================================================
Inicializando banco de dados e aplicando semente de dados...
=================================================================
[+] Categoria criada: Informática (ID: 1)
[+] Categoria criada: Smartphones & Telefonia (ID: 2)
[+] Categoria criada: Móveis para Escritório (ID: 3)
[+] Categoria criada: Áudio & Vídeo (ID: 4)
[+] Produto criado: Mouse Gamer Ergonômico RGB | R$ 149.90 | SKU: INF-MOU-001
...
Sucesso! 4 categorias e 7 produtos inseridos.
=================================================================
```

---

## 7. Comando para Iniciar a Aplicação

Inicie o servidor localmente através do script facilitador:

```bash
python run.py
```

Ou diretamente via Uvicorn:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

O servidor estará operante em: **`http://127.0.0.1:8000`**

---

## 8. Endereços da Documentação Interativa

O FastAPI gera automaticamente a especificação OpenAPI 3.1. Após iniciar o servidor, acesse no navegador:

- **Swagger UI (Interativo):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
  *Permite testar todos os endpoints, autenticar-se e visualizar modelos e códigos de resposta diretamente na interface gráfica.*
- **ReDoc (Documentação técnica detalhada):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 9. Resumo dos Principais Endpoints

| Método | Endpoint | Protegido? | Finalidade |
| :--- | :--- | :---: | :--- |
| **GET** | `/` | Não | Informações e metadados da API |
| **GET** | `/health` | Não | Verificação de integridade operacional |
| **GET** | `/api/v1/categorias` | Não | Listar todas as categorias |
| **POST** | `/api/v1/categorias` | **Sim** | Cadastrar nova categoria |
| **GET** | `/api/v1/produtos` | Não | Listar produtos com suporte a busca, filtros e paginação |
| **GET** | `/api/v1/produtos/{id}` | Não | Consultar produto por ID |
| **POST** | `/api/v1/produtos` | **Sim** | Criar novo produto |
| **PUT** | `/api/v1/produtos/{id}` | **Sim** | Atualização integral de um produto |
| **PATCH** | `/api/v1/produtos/{id}` | **Sim** | Atualização parcial de campos de um produto |
| **DELETE**| `/api/v1/produtos/{id}` | **Sim** | Excluir produto por ID |

---

## 10. Informações para Testar a Autenticação

Para executar operações de escrita (**POST**, **PUT**, **PATCH**, **DELETE**), é necessário fornecer a credencial de acesso.

A API aceita qualquer um dos dois padrões HTTP abaixo:
1. **Cabeçalho Personalizado:**  
   `X-API-Key: uninter_segredo_api_2026`
2. **Cabeçalho Padrão Bearer Token:**  
   `Authorization: Bearer uninter_segredo_api_2026`

Caso o cabeçalho não seja enviado ou o valor seja incorreto, a API responde com status **`401 Unauthorized`**.

---

## 11. Exemplos Práticos de Requisição (cURL)

### 11.1 Listar Produtos com Filtros
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/produtos?categoria_id=1&preco_min=100&preco_max=500" \
     -H "Accept: application/json"
```

### 11.2 Consultar Produto por ID
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/produtos/1" \
     -H "Accept: application/json"
```

### 11.3 Criar Novo Produto (Requer Autenticação)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/produtos" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: uninter_segredo_api_2026" \
     -d '{
       "nome": "SSD NVMe 1TB PCIe 4.0",
       "descricao": "Leitura de 5000MB/s com dissipador",
       "preco": 459.90,
       "estoque": 25,
       "codigo_sku": "INF-SSD-004",
       "categoria_id": 1,
       "ativo": true
     }'
```

### 11.4 Atualizar Parcialmente um Produto (PATCH)
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/produtos/1" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: uninter_segredo_api_2026" \
     -d '{
       "preco": 139.90,
       "estoque": 50
     }'
```

### 11.5 Excluir Produto (DELETE)
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/produtos/7" \
     -H "X-API-Key: uninter_segredo_api_2026"
```

---

## 12. Execução dos Testes Automatizados

O projeto conta com uma suíte de 27 testes automatizados cobrindo todos os endpoints, status HTTP, validações e regras de segurança:

```bash
python -m pytest tests/test_api.py -v
```

Para executar a demonstração automática com saída formatada de todas as requisições no console:

```bash
python test_requests.py
```
