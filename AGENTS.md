# Aranae — Global Rules

## Project
Aranae is a job market intelligence platform.
Pipeline: Scrape → Ingest Raw → dbt Transform → Streamlit Dashboard.
Stack: Python 3.13, PostgreSQL, dbt-core, Dagster, Pydantic, Streamlit.

## Architecture (ELT)
- `scrapers/`          → Scraping logic and URL configs (`config.py`, `utils.py`)
- `services/`          → Shared services (`ingestor.py`, `transformers.py`, `db.py`)
- `models/schemas.py`  → Pydantic `JobSchema` (source of truth for all job data)
- `dbt/models/source/` → Staging models (`stg_*.sql`): normalize dates, income, contracts, remote, experience
- `dbt/models/mart/`   → `fct_jobs.sql`: final unified view across all sources
- `dbt/macros/`        → Reusable SQL macros (`normalize_date`, `extract_income`, `format_wttj_salary`, etc.)
- `dagster_app/`       → Pipeline orchestration (in progress)

## Non-negotiable Rules
- NEVER hardcode credentials or API keys. Use `.env` + `dotenv run`.
- NEVER modify `RAW_*` tables directly. Raw data is append-only and immutable.
- NEVER duplicate logic. Check `scrapers/utils.py` and `dbt/macros/` first.
- ALWAYS validate output against `models/schemas.py` before ingestion.
- ALWAYS make atomic, single-purpose commits with a concise one-line message (e.g. `feat: add wttj scraper`).

## Security
- NEVER print, log, echo, or display credentials, API keys, tokens, or passwords in output.
- NEVER commit `.env`, `*.pem`, `*.key`, or any file containing secrets. Only `.env.example` (with placeholder values) is committed.
- NEVER pass secrets as CLI arguments (visible in `ps` / shell history). Use `dotenv run` or env vars.
- NEVER store secrets in source code, comments, docstrings, or config files tracked by Git.
- ALL new env variables MUST be documented in `.env.example` with a placeholder (e.g. `MY_API_KEY=your_key_here`).
- Database credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`) and `MISTRAL_API_KEY` live exclusively in `.env`.
- When writing bash commands that need credentials, ALWAYS use `dotenv run -- <command>`. Never `export VAR=value`.
- If a new external service requires an API key, add it to `.env` + `.env.example` and access it via `os.getenv()` in Python.

## Environment
- Activate venv: `source venv/bin/activate`
- Run commands: `dotenv run -- python scrapers/freework_scraper.py`
- Run dbt: `dotenv run -- dbt run --project-dir dbt --profiles-dir dbt`

## Key Files (lazy-load on need)
When working on scraping: read `scrapers/utils.py`, `scrapers/config.py`, `services/transformers.py`.
When working on dbt: read `dbt/macros/*.sql`, `dbt/models/source/*/stg_*.sql`.
