# Motorola Community Scanner

Sistema web para varredura automatica da comunidade Motorola no forum da Lenovo, extracao de reclamacoes e geracao de casos de teste com LLM local via Ollama.

## Escopo do produto
- Fonte fixa e obrigatoria: `https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity`
- Sem entrada manual de URL no fluxo principal.
- Apenas paginas publicas sem autenticacao.

## Status atual
Implementacao em fases.

- Fase 1: concluida
- Fase 2: concluida
- Fase 3: concluida
- Fases 4 a 7: pendentes

## O que foi entregue ate a Fase 3
- Monorepo inicial (`backend`, `frontend`, `docs`, `docker`).
- Backend FastAPI com SQLAlchemy + Celery + Redis + PostgreSQL.
- Modelos SQLAlchemy base: `ScanExecution`, `Topic`, `TestCase`.
- Endpoint `POST /api/v1/scan/start` para iniciar varredura sem URL manual.
- Uso obrigatorio da URL fixa da comunidade Motorola no backend.
- Endpoint `GET /api/v1/scan/latest` com resumo da ultima execucao.
- Descoberta automatica de links da comunidade Motorola com paginação e deduplicacao.
- Classificacao de links em `topic`, `listing` e `irrelevant` especifica para Lenovo Motorola Community.
- Persistencia dos topicos candidatos em `topics` com metadados de origem da descoberta.
- Frontend com botao unico funcional:
  - "Iniciar varredura da comunidade Motorola"
  - Chama `POST /scan/start` e mostra status/resumo da ultima execucao.
- Dockerfiles e `docker-compose.yml`.
- Testes iniciais com pytest e Vitest.

## Estrutura do monorepo
```text
.
|-- AGENTS.md
|-- README.md
|-- .env.example
|-- docker-compose.yml
|-- backend
|   |-- app
|   |   |-- api
|   |   |-- core
|   |   |-- db
|   |   |-- integrations
|   |   |-- models
|   |   |-- schemas
|   |   |-- services
|   |   `-- workers
|   |-- requirements.txt
|   `-- tests
|-- frontend
|   |-- src
|   `-- tests
|-- docs
|   |-- architecture.md
|   `-- phases.md
`-- docker
    |-- backend.Dockerfile
    `-- frontend.Dockerfile
```

## Requisitos
- Docker + Docker Compose

Opcional sem Docker:
- Python 3.12+
- Node.js 22+

## Configuracao de ambiente
1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
2. Ajuste chaves e URLs conforme necessario.

## Subir o ambiente (Docker)
```bash
docker compose up --build
```

Servicos:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Endpoints disponiveis ate a Fase 3
- `GET /api/v1/health`
- `POST /api/v1/scan/start`
- `GET /api/v1/scan/latest`
- `GET /api/v1/topics` (placeholder)

## Fluxo da Fase 3
1. Usuario acessa a tela principal.
2. Usuario clica em "Iniciar varredura da comunidade Motorola".
3. Frontend chama `POST /api/v1/scan/start` sem body.
4. Backend cria `ScanExecution` com a URL fixa da comunidade Motorola.
5. Backend enfileira tarefa no Celery.
6. Worker executa descoberta de links e persiste topicos candidatos.
7. Frontend consulta `GET /api/v1/scan/latest` para mostrar o resumo.

## Executar testes
### Backend (pytest)
```bash
cd backend
pytest
```

### Frontend (Vitest)
```bash
cd frontend
npm install
npm run test
```

## Arquitetura
Detalhes em [docs/architecture.md](./docs/architecture.md).

## Plano por fases
1. Fase 1: base do monorepo e infraestrutura (concluida)
2. Fase 2: start de scan com URL fixa e botao funcional (concluida)
3. Fase 3: descoberta e classificacao de links (concluida)
4. Fase 4: scraping detalhado e extracao estruturada
5. Fase 5: integracao Ollama e geracao de testes
6. Fase 6: dashboard completo e exportacoes
7. Fase 7: robustez final, testes ampliados e seeds
