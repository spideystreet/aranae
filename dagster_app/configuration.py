
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Postgres Configuration
PG_USER = os.getenv("POSTGRES_USER", "synapse_user")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "synapse_password")
PG_DB = os.getenv("POSTGRES_DB", "synapse_db")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
FREEWORK_URL = os.getenv("FREEWORK_URL", "https://www.free-work.com/fr/tech-it/jobs")
