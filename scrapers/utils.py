import json
import random
import time

from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_headers() -> dict:
    """Returns standard headers for requests."""
    return DEFAULT_HEADERS


def polite_sleep(min_delay: float = 1.0, max_delay: float = 2.5):
    """Wait for a random duration to be polite to servers."""
    time.sleep(random.uniform(min_delay, max_delay))


def extract_json_ld(soup: BeautifulSoup) -> dict | None:
    """
    Extracts JobPosting JSON-LD from a BeautifulSoup object.
    Returns the first JobPosting object found or None.
    """
    ld_scripts = soup.select('script[type="application/ld+json"]')
    for s in ld_scripts:
        try:
            data = json.loads(s.get_text())
            if isinstance(data, list):
                data = data[0]
            if data.get("@type") == "JobPosting":
                return data
        except (json.JSONDecodeError, IndexError, AttributeError):
            continue
    return None


def init_job_details() -> dict:
    """Initializes the standard job details dictionary structure."""
    return {
        "job_id": None,
        "title": None,
        "company": None,
        "publication_date": None,
        "location": None,
        "city": None,
        "region": None,
        "income": None,
        "skills": [],
        "contracts": [],
        "duration": None,
        "experience_level": None,
        "start_date": None,
        "remote": None,
        "description": None,
        "url": None,
        "source": None,
    }
