applyTo: '**'

Estilo de respostas (sempre em Português, didático e conciso)
- Responder em PT‑BR, em tom profissional, claro e direto.
- Priorizar exemplos práticos e passos acionáveis.
- Manter as respostas curtas; usar listas quando ajudar a escanear.
- Evitar jargões desnecessários; explicar termos quando aparecerem.
- Quando houver riscos, apontar rapidamente e sugerir a opção segura.

Preferências e convenções do repositório
- Código e nomes (módulos, classes, funções, variáveis, endpoints, schemas, tabelas) em inglês.
- Documentação de uso/README em PT‑BR; comentários em código preferencialmente em inglês.
- Padrões Python: snake_case (funções/variáveis), PascalCase (classes), UPPER_SNAKE_CASE (constantes).
- SQLAlchemy 2.x: usar select()/scalars(), lazy='selectin' em relacionamentos, AsyncSession.
- FastAPI: routers finos; dependências via Annotated/Depends; validações com Pydantic Schemas.
- Segurança: JWT via create_access_token, senha com pwdlib. Não logar segredos.

Testes e qualidade
- Ao propor mudanças públicas, sugerir testes mínimos (happy path + 1 edge) em pytest.
- Usar Testcontainers para integração com Postgres quando aplicável.
- Rodar/indicar: poetry run task test, alembic upgrade head se schema mudar.
- Sugerir ruff para lint/format.

Quando gerar código
- Respeitar imports existentes (re-exports em backend/models e backend/schemas).
- Não quebrar a API pública existente; se precisar, indicar migração simples.
- Usar tipos e validações claras nos Schemas; mapear ORM → Pydantic com ConfigDict(from_attributes=True).

Quando pedirem exemplos de uso da API
- Mostrar rapidamente: criar usuário, obter token em /auth/token, usar Bearer em endpoints protegidos.
- Indicar URLs padrão: http://localhost:8000 e docs em /docs.

Notas finais
- Se faltar contexto, sugerir 1-2 suposições razoáveis e prosseguir, avisando.
- Nunca expor credenciais; usar variáveis de ambiente.
