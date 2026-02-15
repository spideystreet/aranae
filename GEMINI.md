# Synapse - Project Context & Guidelines

## 1. Project Overview
Synapse is a data scraping and processing pipeline designed to collect, clean, and store job offers from various platforms (e.g., Free-Work).

## 2. Tech Stack
- **Python**: Core logic.
- **PostgreSQL**: Primary data store for jobs and raw HTML.
- **Dagster** (Planned): For pipeline orchestration.

## 3. Architecture
- **Scrapers**: Modules responsible for fetching and parsing HTML from job boards.
- **Database Service**: `services/database.py` for all PostgreSQL interactions.
- **Data Model**: Structured storage of job titles, companies, locations, dates, and descriptions.

## 4. Current State
- Database connection and basic job fetching logic implemented.
- Initial research on prompt-based cleaning performed (later simplified/removed).

## 5. Development Rules
- **Structure**: Maintain a clean separation between scrapers, services, and orchestration.
- **Database**: Always use the centralized `database.py` service.
- **Code Quality**: Ensure clear documentation and error handling in all scraping logic.
