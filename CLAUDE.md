# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Aranae is a job market intelligence platform. Pipeline: **Scrape → Ingest Raw → dbt Transform → Streamlit Dashboard**.

Stack: Python 3.13, PostgreSQL (port 5434), dbt-core, Dagster, Pydantic, Streamlit.

## Commands

```bash
# Install dependencies (first time or after pyproject.toml changes)
uv sync --dev

# Activate environment
source .venv/bin/activate

# Start database
docker compose up -d

# Initialize DB tables (first time)
dotenv run -- python scripts/setup_db.py

# Run scrapers
dotenv run -- python scrapers/freework_scraper.py
dotenv run -- python scrapers/wttj_scraper.py

# Run dbt transformations
dotenv run -- dbt run --project-dir dbt --profiles-dir dbt
dotenv run -- dbt test --project-dir dbt --profiles-dir dbt

# Run a single dbt model
dotenv run -- dbt run --project-dir dbt --profiles-dir dbt --select <model_name>

# Start Dagster UI (orchestration)
dotenv run -- dagster dev

# Start Streamlit dashboard
dotenv run -- streamlit run dashboard.py
```

**Always prefix commands with `dotenv run --`** — never export credentials to the shell.

## Architecture

```
scrapers/           Scraping logic per source (freework_scraper.py, wttj_scraper.py)
  config.py         Base URLs for each source
  utils.py          Shared helpers: get_headers(), polite_sleep(), extract_json_ld(), init_job_details()
services/
  db.py             get_db_connection() — single connection factory
  ingestor.py       ingest_jobs(jobs, table_name) — validates via Pydantic then upserts
  transformers.py   Source-specific data cleaning before ingestion
models/
  schemas.py        JobSchema (Pydantic) — source of truth for all job fields
dagster_app/
  assets/ingestion.py   Dagster assets that call scrapers → return DataFrames
  assets/dbt.py         Dagster asset that runs dbt build
  definitions.py        Wires assets, resources, and daily schedule
  constants.py          DBT_PROJECT path constant
dbt/
  models/source/    Staging models per source (stg_freework.sql, stg_wttj.sql): normalize dates, income, contracts, remote, experience
  models/mart/      fct_jobs.sql — unified view across all sources
  macros/           Reusable SQL: normalize_date, extract_income, format_wttj_salary, normalize_experience
dashboard.py        Streamlit app — reads from fct_jobs and sources_metadatas
```

### Data flow

1. Scrapers produce a list of dicts matching `init_job_details()` shape
2. `ingest_jobs()` validates each dict via `JobSchema`, converts lists to comma-separated strings, upserts into `RAW_FREEWORK` or `RAW_WTTJ`
3. dbt staging models normalize raw text fields into structured data
4. `fct_jobs` unifies all sources into one mart table
5. Dashboard reads from `fct_jobs` (with `salary`, `tjm` columns from dbt transforms)

### Raw tables

`RAW_FREEWORK` and `RAW_WTTJ` have a `UNIQUE (source, job_id)` constraint. The ingestor uses `ON CONFLICT DO UPDATE` (upsert). **Never modify raw tables directly — they are append-only.**

## Key conventions

- **Adding a scraper**: reuse `scrapers/utils.py` helpers; validate output against `models/schemas.py`; ingest via `services/ingestor.py`
- **Adding dbt logic**: check `dbt/macros/` before writing new SQL — normalization macros already exist
- **Credentials**: all in `.env`, accessed via `os.getenv()`. Any new env var must also appear in `.env.example` with a placeholder
- **Commits**: atomic, single-purpose, conventional format (e.g. `feat: add linkedin scraper`)
