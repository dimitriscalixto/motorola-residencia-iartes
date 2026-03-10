# Status das fases

## Fase 1 (concluida)
- Monorepo base (`backend`, `frontend`, `docs`, `docker`).
- Backend FastAPI com SQLAlchemy, Pydantic Settings, Celery, Redis e PostgreSQL (via docker-compose).
- Modelos iniciais: `ScanExecution`, `Topic`, `TestCase`.
- Shell inicial de frontend React/Vite/TS.
- Dockerfiles e `docker-compose.yml`.
- `README`, `.env.example`, `AGENTS.md`.

## Fase 2 (concluida)
- URL fixa da comunidade Motorola aplicada no fluxo real.
- Implementacao de `POST /scan/start`.
- Criacao de `ScanExecution` sem input manual de URL.
- Enfileiramento assincrono via Celery para iniciar execucao.
- Implementacao de `GET /scan/latest`.
- Botao unico no frontend chamando o endpoint de inicio.

## Fase 3 (concluida)
- Implementacao de `link_classifier.py` com regras especificas de `topic`, `listing` e `irrelevant`.
- Implementacao de `discovery_service.py` com deduplicacao e persistencia de candidatos.
- Descoberta iniciando da URL fixa da comunidade Motorola.
- Navegacao de listagens/paginacao via Firecrawl map com fallback HTTP.
- Persistencia dos topicos descobertos em `topics` com rastreabilidade da origem.
- Atualizacao de contadores em `ScanExecution` (`discovered_links_count` e `valid_topics_count`).

## Fases 4 a 7 (pendentes)
- Scraping detalhado e extracao estruturada.
- Integracao Ollama com validacao JSON e retries.
- Dashboard completo, exportacoes, robustez final e testes ampliados.
