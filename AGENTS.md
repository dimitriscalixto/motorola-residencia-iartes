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

### Proxima fase obrigatoria
### Fase 3
- Implementar `discovery_service.py` com descoberta real de links.
- Implementar `link_classifier.py` com regras especificas da comunidade Motorola.
- Persistir candidatos de topico deduplicados.
- Atualizar contadores da execucao.

## Convencoes
- Servicos por responsabilidade em `backend/app/services`.
- Integracoes externas em `backend/app/integrations`.
- Endpoints em `backend/app/api/routes`.
- Codigo novo com tipagem consistente.
- Nao introduzir scraping generico para outros dominios.

## Decisoes tecnicas
- Bootstrap de banco por `Base.metadata.create_all` no startup para simplificar setup inicial.
- Na Fase 2, o worker de scan ainda e placeholder (inicia e finaliza sem discovery real).
- CORS liberado para `localhost:5173` e `127.0.0.1:5173` para integracao local frontend/backend.

