# Arquitetura (Fases 1 a 3)

## Visao geral
O projeto e um monorepo com separacao entre backend, frontend e infraestrutura Docker.

- `backend`: API FastAPI, modelos SQLAlchemy, configuracao de banco, Celery e servicos por responsabilidade.
- `frontend`: app React + Vite + TypeScript com acao principal de inicio de varredura.
- `docs`: documentacao tecnica e acompanhamento das fases.
- `docker`: imagens Docker de backend e frontend.

## Backend
Estrutura principal:

- `app/main.py`: inicializacao do FastAPI, lifespan e CORS.
- `app/core/config.py`: leitura de variaveis de ambiente via Pydantic Settings.
- `app/db/*`: engine, sessao e bootstrap do banco.
- `app/models/*`: entidades `ScanExecution`, `Topic`, `TestCase`.
- `app/api/*`: roteamento e endpoints REST.
- `app/core/celery_app.py`: configuracao da fila Celery (Redis).
- `app/workers/tasks.py`: tarefas assicronas do worker.
- `app/services/*`: servicos por responsabilidade.
- `app/integrations/*`: clientes externos (Firecrawl com descoberta na Fase 3, Ollama para fase futura).

## Frontend
Estrutura principal:

- `src/App.tsx`: tela principal com botao unico para iniciar varredura.
- `src/styles.css`: estilo base responsivo.
- `tests/*`: testes iniciais com Vitest.

## Banco de dados
Modelos base:

- `scan_executions`
- `topics`
- `test_cases`

Bootstrap atual: `Base.metadata.create_all` no startup da API.

## Fluxo implementado ate a Fase 3
1. Frontend chama `POST /api/v1/scan/start`.
2. Backend cria `ScanExecution` com fonte fixa da comunidade Motorola.
3. Backend enfileira tarefa no Celery.
4. Worker executa descoberta de links de listagem/subtopicos.
5. `LinkClassifier` classifica URLs em `topic`, `listing` e `irrelevant`.
6. `DiscoveryService` deduplica e persiste topicos candidatos em `topics`.
7. `ScanExecution` recebe contadores de descoberta atualizados.
8. Frontend consulta `GET /api/v1/scan/latest` para atualizar resumo.

## Pipeline planejado (fases seguintes)
1. Fazer scraping detalhado de topicos e extracao estruturada.
2. Gerar casos de teste com Ollama local.
3. Exibir progresso detalhado, listagem, detalhe e exportacoes.
