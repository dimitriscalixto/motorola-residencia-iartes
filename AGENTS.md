# AGENTS - Motorola Community Scanner

## Fonte de verdade do projeto
Este arquivo registra o estado de implementacao e as decisoes de arquitetura para continuidade.

## Escopo fixo do produto
- Fonte obrigatoria: `https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity`
- Nao ha entrada manual de URL no fluxo principal.
- Apenas paginas publicas sem autenticacao.

## Stack obrigatoria
- Backend: Python, FastAPI, SQLAlchemy, Pydantic, Celery, Redis, PostgreSQL
- Frontend: React, Vite, TypeScript
- Integracoes: Firecrawl, Ollama
- Infra: Docker + docker-compose

## Estado atual
### Fase 1: concluida
- Monorepo inicial criado.
- Backend estruturado e executavel com FastAPI.
- Modelos SQLAlchemy base criados (`ScanExecution`, `Topic`, `TestCase`).
- Celery + Redis preparados.
- Frontend shell criado com UI inicial.
- Dockerfiles + docker-compose configurados.
- Documentacao inicial criada.

### Fase 2: concluida
- `POST /api/v1/scan/start` implementado.
- `ScanExecution` criado com URL fixa da comunidade Motorola.
- Inicio da execucao sem input manual de URL.
- Disparo assincrono de tarefa via Celery.
- `GET /api/v1/scan/latest` implementado.
- Botao principal do frontend conectado ao endpoint.

### Fase 3: concluida
- `link_classifier.py` implementado com regras especificas para Motorola Community.
- `discovery_service.py` implementado com deduplicacao e persistencia de candidatos.
- Descoberta de links iniciando da URL fixa com Firecrawl map + fallback HTTP.
- Persistencia de topicos candidatos em `topics` com metadados de origem.
- Atualizacao de contadores da execucao (`discovered_links_count`, `valid_topics_count`).

### Proxima fase obrigatoria
### Fase 4
- Implementar `topic_scraper_service.py`.
- Implementar scraping detalhado em `firecrawl_client.py::scrape_topic`.
- Implementar `extraction_service.py` para extracao estruturada e confidence score.
- Persistir `raw_content` e metadados de extracao por topico.

## Convencoes
- Servicos por responsabilidade em `backend/app/services`.
- Integracoes externas em `backend/app/integrations`.
- Endpoints em `backend/app/api/routes`.
- Codigo novo com tipagem consistente.
- Nao introduzir scraping generico para outros dominios.

## Decisoes tecnicas
- Bootstrap de banco por `Base.metadata.create_all` no startup para simplificar setup inicial.
- Na Fase 3, o worker de scan passou a executar descoberta e persistencia de topicos candidatos.
- CORS liberado para `localhost:5173` e `127.0.0.1:5173` para integracao local frontend/backend.
