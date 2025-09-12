applyTo: '**'
Projeto base: contexto e diretrizes

Resumo do projeto
- API em FastAPI com autenticação JWT, domínio de usuários e exemplo de CRUD (todos) apenas como referência.
- SQLAlchemy 2.x (async) com Alembic para migrações.
- Psycopg 3 para PostgreSQL.
- Pydantic Settings para configuração via `.env`.
- Testes com Pytest, pytest-asyncio e Testcontainers (Postgres). Cobertura com coverage.
- Docker/Compose para dev e execução.

Arquitetura (alto nível)
- Camadas principais:
	- Routers (`backend/routers/`): endpoints HTTP; manter handlers finos, sem regra de negócio pesada.
	- Models (`backend/models/`): entidades SQLAlchemy por domínio (`user.py`, `todo.py`, `base.py` com `table_registry` e `TodoState`).
	- Schemas (`backend/schemas/`): DTOs Pydantic por domínio (`users.py`, `auth.py`, `common.py`, `todos.py`).
	- Segurança (`backend/security.py`): JWT, hashing e dependências para autenticação.
	- Banco (`backend/database.py`): engine async e `get_session()` como dependência.
	- Configurações (`backend/settings.py`): `Settings` via Pydantic Settings.
- Re-exports em `backend/models/__init__.py` e `backend/schemas/__init__.py` para importes estáveis:
	- Ex.: `from backend.models import User, TodoState` e `from backend.schemas import UserPublic`.

Autenticação e usuários
- Fluxo OAuth2 com senha:
	- `POST /auth/token` recebe `username` (email) e `password` (form OAuth2) e retorna `access_token` (JWT).
	- `POST /auth/refresh_token` retorna um novo token usando o usuário autenticado.
- JWT:
	- Criado por `create_access_token(data)` em `backend/security.py` com expiração via `ACCESS_TOKEN_EXPIRE_MINUTES`.
	- Validado por `get_current_user(...)`, que decodifica JWT e carrega `User` por email; lança 401 para token inválido/expirado.
- Senhas:
	- Hash e verificação com `pwdlib.PasswordHash.recommended()` (`get_password_hash`/`verify_password`).
- Usuários:
	- Endpoints: criar, listar com paginação (offset/limit), atualizar e excluir (validando permissão: usuário só altera/exclui a si mesmo).

Diretrizes de código
- Routers finos: delegar regra de negócio para serviços (quando crescer) e reuso de dependências (ex.: `get_session`, `get_current_user`).
- Schemas explícitos: separar entrada (ex.: `UserSchema`) e saída (ex.: `UserPublic`). Use `model_config = ConfigDict(from_attributes=True)` para mapear ORM → Pydantic.
- Filtros/paginação: usar `FilterPage`/`FilterTodo` como referência para paginar e filtrar via Query params.
- SQLAlchemy 2.x: preferir `select()`/`scalars()`; usar `lazy='selectin'` em relacionamentos para eficiência.
- Migrações: manter Alembic sincronizado com `alembic revision` e `upgrade head` ao evoluir models.
- Segurança: nunca registrar segredos; validar expiração do JWT; retornar 401 de forma consistente.
- Tratamento de erros: usar HTTPException com mensagens claras e status apropriados.

Linguagem, nomenclatura e estilo
- Idioma
	- Conversas, respostas do assistente e documentação de uso (README) em Português (PT‑BR).
	- Nomes de código DEVEM ser em inglês: módulos/arquivos, classes, funções, variáveis, endpoints/paths, schemas, tabelas, colunas, chaves/constraints e nomes de migrações.
	- Mensagens de erro retornadas pela API preferencialmente em inglês para consistência técnica (salvo decisão de produto em contrário).
- Convenções
	- Python: snake_case para funções/variáveis; PascalCase para classes; UPPER_SNAKE_CASE para constantes.
	- FastAPI: endpoints e tags em inglês; prefixos de rotas no plural quando fizer sentido.
	- Banco: tabelas em snake_case no plural; colunas em snake_case; chaves/constraints com prefixo (`pk_`, `fk_`, `uq_`).
	- Commits e mensagens de PR preferencialmente em inglês (curtas e descritivas).
	- Comentários em código preferencialmente em inglês; docs do projeto podem ser PT‑BR.

Testes
- Testcontainers com Postgres para testes de integração (isola banco por engine de sessão):
	- `conftest.py` cria `engine` com container Postgres e session async por teste.
	- Tabelas são criadas/derrubadas entre testes usando `table_registry.metadata`.
	- `TestClient` com `dependency_overrides` para injetar a sessão de teste.
- Factories com `factory_boy` (`UserFactory`) para criar dados previsíveis.
- Cobrir cenários de autenticação (login, refresh, 401) e CRUD de usuários (conflitos, permissões, paginação).

Compose e Postgres (saúde e conflitos)
- Healthcheck do Postgres usa `pg_isready -U $POSTGRES_USER -d $POSTGRES_DB`.
- Se aparecer “role root” ou o healthcheck falhar, verifique a linha `test` do healthcheck e variáveis do serviço.
- Conflitos de porta 5432 no Windows: se houver Postgres nativo rodando, pare o serviço ou mude a porta do Compose.
- Evite perder dados: use `docker compose down` (sem `-v`); `-v` apaga o volume (reset do banco).
