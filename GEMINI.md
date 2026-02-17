# Synapse - Project Context & Guidelines

## 1. Project Overview
Synapse is a data scraping and processing pipeline designed to collect, clean, and store job offers from various platforms (Free-Work and Welcome to the Jungle).

## 2. Tech Stack
- **Python**: Core logic and scrapers.
- **PostgreSQL**: Primary data store.
- **dbt**: Data transformation layer (ELT).
- **Streamlit**: Data visualization dashboard.
- **Dagster**: Orchestration (In progress).

## 3. Architecture (ELT)
- **Scrapers**: `scrapers/*_scraper.py`. High-fidelity extraction (WTTJ uses `__INITIAL_DATA__` for deep extraction).
- **RAW Layer**: Tables `RAW_FREEWORK` and `RAW_WTTJ` contains strictly raw data from sources. **No mapping or cleaning allowed here.**
- **Staging Layer (dbt)**: `stg_*` models handle normalization (dates, income, contracts, remote, experience).
- **Mart Layer (dbt)**: `fct_jobs` unified view for all platforms.
- **Metadata**: Managed via dbt seeds (`sources_metadatas.csv`).

## 4. Current State
- Robust scraping for Free-Work and WTTJ implemented.
- dbt project configured with global `table` materialization.
- Unified dashboard with filtration and platform icons.
- Standardized mapping for Remote Work (`Télétravail 100%`, `Télétravail partiel`, `Présentiel`, `Pas d'infos`).

## 5. Development Rules
- **ELT Flow**: Scrapers load raw ➔ Staging normalizes ➔ Pivot/Mart aggregates.
- **Scrapers**: Follow naming convention `[source]_scraper.py`. Use `services/ingestor.py` for all DB ingestion.
- **Dbt**: 
    - Use macros for repetitive logic (`normalize_experience`, `normalize_date`, `extract_income`).
    - Keep materialization as `table` (set globally in `dbt_project.yml`).
    - Use seeds for static reference data.
- **Git**: Ensure `.user.yml`, `.env`, `scripts/`, and `.streamlit/` are ignored. Always use atomic commits.
