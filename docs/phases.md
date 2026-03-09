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

## Fases 3 a 7 (pendentes)
- Descoberta e classificacao de links.
- Scraping detalhado e extracao estruturada.
- Integracao Ollama com validacao JSON e retries.
- Dashboard completo, exportacoes, robustez final e testes ampliados.

