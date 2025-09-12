# Base FastAPI – Backend

Projeto base para APIs com FastAPI, SQLAlchemy 2.x (async), Alembic, autenticação JWT e Docker. Pensado para ser clonado/duplicado e iniciar rápido.

## Stack

- FastAPI (fastapi[standard])
- SQLAlchemy 2.x (async) + Alembic
- Psycopg 3 (PostgreSQL)
- Pydantic Settings (.env)
- Poetry (dependências e tasks)
- Ruff, Pytest (+ pytest-asyncio, coverage)
- Docker e Docker Compose

## Estrutura do projeto

- `backend/`
  - `app.py` (FastAPI app)
  - `routers/` (rotas: `auth.py`, `users.py`, `todos.py`)
  - `models/` (domínios: `base.py`, `user.py`, `todo.py` e `__init__.py` com re-exports)
  - `schemas/` (domínios: `common.py`, `auth.py`, `users.py`, `todos.py` e `__init__.py` com re-exports)
  - `security.py` (JWT, senha e dependências de auth)
  - `database.py` (engine e sessão async)
  - `settings.py` (configurações via `.env`)
- `migrations/` (scripts Alembic)
- `alembic.ini` (configuração Alembic)
- `pyproject.toml` (dependências, linters, tasks)
- `compose.yaml` (serviços Docker)
- `Dockerfile` (imagem do app)
- `tests/` (testes)

## Pré‑requisitos

- Python 3.13
- Poetry
- Docker Desktop (para Docker/Compose e testcontainers)

## Configuração inicial

1) Instale as dependências:
```bash
poetry env use 3.13
poetry install
```

2) Crie o `.env` na raiz do projeto:
```env
DATABASE_URL="postgresql+psycopg://app_user:app_password@127.0.0.1:5432/app_db"
SECRET_KEY="troque-isto"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
Observação: no Docker Compose, o `DATABASE_URL` pode apontar para o serviço `backend_database`.

## Desenvolvimento rápido (DB no Docker, app local) — recomendado

Fluxo otimizado para iterar no código do app usando o Postgres em container e o servidor FastAPI local.

1) Subir só o banco:
```bash
chmod +x entrypoint.sh # Verificar se precisa (Testar antes sem)
docker compose up -d backend_database
```

2) Verificar se o banco está pronto:
```bash
docker compose logs -f backend_database
```
Procure por “database system is ready to accept connections”.

3) Ajustar o `.env` para apontar para o host:
```env
DATABASE_URL="postgresql+psycopg://app_user:app_password@127.0.0.1:5432/app_db"
```

4) Rodar migrações localmente (se necessário):
```bash
poetry run alembic upgrade head
```

5) Rodar o app local com reload:
```bash
poetry run task run
```
Docs em http://localhost:8000/docs

6) Parar o banco (mantendo dados):
```bash
docker compose down
```
Para resetar os dados deste projeto:
```bash
docker compose down -v
```

## Outras formas de rodar

### 1) Docker Compose (app + Postgres)

Suba tudo com Compose.
```bash
docker compose up -d
docker compose logs -f backend_app
```
A API sobe em http://localhost:8000. O Postgres expõe 5432.

Rodar migrações dentro do container do app:
```bash
docker compose exec backend_app poetry run alembic upgrade head
```

Finalizar:
```bash
docker compose down      # mantém dados
docker compose down -v   # apaga dados (volume)
```

### 2) Local puro (Poetry + Postgres local)

Use um Postgres local na porta 5432 e rode tudo via Poetry.
```bash
poetry env use 3.13
poetry install
poetry run alembic upgrade head
poetry run task run
```

### 3) Build de imagem manual

```bash
docker build -t fastapi_backend .
```

## Migrações Alembic

- Subir para a cabeça:
```bash
alembic upgrade head
```
- Criar nova revisão:
```bash
alembic revision -m "minha mudança"
```

## Testes

Execute a suíte:
```bash
poetry run task test
```
Se os testes usarem testcontainers, abra o Docker Desktop antes.

## Utilitários do projeto (rápido e direto)

- `backend.settings.Settings`
  - Lê variáveis do `.env` via Pydantic Settings:
    - `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.

- `backend.database.get_session()`
  - Dependência que fornece `AsyncSession` (SQLAlchemy async) usando `Settings().DATABASE_URL`.
  - Uso em rotas: `Session = Annotated[AsyncSession, Depends(get_session)]`.

- `backend.security`
  - `create_access_token(data)` – Gera JWT com expiração configurável.
  - `get_password_hash(password)` / `verify_password(plain, hashed)` – Hash e verificação de senha.
  - `get_current_user(...)` – Dependência que valida o Bearer token, decodifica o JWT e carrega o usuário; lança 401 quando inválido/expirado.
  - OAuth2: `OAuth2PasswordBearer(tokenUrl='auth/token', refreshUrl='auth/refresh')`. O refresh está em `POST /auth/refresh_token`.

## Endpoints principais

- Auth
  - `POST /auth/token` – Login com `username` (email) e `password` (OAuth2 form). Retorna `access_token`.
  - `POST /auth/refresh_token` – Retorna novo `access_token` para o usuário autenticado.
- Users
  - `POST /users/` – Cria usuário (hash de senha, checa duplicidade de username/email).
  - `GET /users/` – Lista com paginação por offset/limit.
  - `PUT /users/{user_id}` – Atualiza o próprio usuário (valida permissão).
  - `DELETE /users/{user_id}` – Exclui o próprio usuário.
- Todos (requer Bearer token)
  - `POST /todos/` – Cria.
  - `GET /todos/` – Lista com filtros (`title`, `description`, `state`) e paginação.
  - `PATCH /todos/{todo_id}` – Atualiza campos parciais.
  - `DELETE /todos/{todo_id}` – Remove.

## Usar como template

1) No GitHub, clique em “Use this template” e crie seu novo repositório.

2) Clone e entre na pasta:
```bash
git clone <url-do-novo-repo>
cd <pasta-do-novo-repo>
```

3) Ajuste metadados:
- Edite o nome da pasta do projeto `FastAPI-Project-Base` → `backend_(nome do projeto)`.
- Não renomeie a pasta `backend` (o app continua `backend.app:app`).

4) Crie o `.env` (exemplo acima) e siga o fluxo recomendado:
- Desenvolvimento rápido (DB no Docker, app local)
  ```bash
  docker compose up -d backend_database
  poetry install
  poetry run alembic upgrade head
  poetry run task run
  ```

5) Persistência de dados
- Cada projeto/pasta cria um volume próprio (ex.: `<nome>_pgdata`).
- Para manter dados: `docker compose down`.
- Para resetar: `docker compose down -v`.

## Solução de problemas (Windows)

- Porta 5432 em uso (Postgres nativo vs Docker):
  - Pare o serviço “PostgreSQL …” no Services (services.msc) ou mude a porta.
  - Veja quem escuta a porta: `netstat -ano | findstr ":5432"`.

- Alembic/psycopg: “password authentication failed”
  - Geralmente `DATABASE_URL` apontando pro banco errado; confira `.env` e `compose`.

- Testcontainers não encontra Docker (npipe … não encontrado)
  - Abra/reenicie o Docker Desktop e valide com `docker ps`.

- “exec format error” em scripts no container
  - Garanta shebang `#!/usr/bin/env sh` e finais de linha LF no `entrypoint.sh`. Se preciso, normalize no build e `chmod +x`.

