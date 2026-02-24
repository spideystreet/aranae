import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import random
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from scrapers.config import WTTJ_BASE_URL
from services.ingestor import ingest_jobs
from services.transformers import build_wttj_job_payload


def fetch_wttj_details(url: str) -> dict:
    """
    Fetches details from a WTTJ job page by extracting window.__INITIAL_DATA__.
    This is much more reliable and contains all metadata (income, remote, etc.)
    """
    details = {
        "location": None,
        "city": None,
        "region": None,
        "income": None,
        "duration": None,
        "experience_level": None,
        "company": None,
        "description": None,
        "start_date": None,
        "publication_date": None,
        "title": None,
        "contracts": [],
        "skills": [],
        "remote": None,
    }

    if not url:
        return details

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return details

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # 1. Strategy: Extract from window.__INITIAL_DATA__
        script_tag = soup.find("script", string=re.compile(r"window\.__INITIAL_DATA__\s*="))
        if script_tag:
            try:
                # Extract the JSON string between double quotes
                script_content = script_tag.string
                json_match = re.search(r'window\.__INITIAL_DATA__\s*=\s*"(.*)"', script_content)
                if json_match:
                    # The JSON is escaped inside a JS string
                    escaped_json = json_match.group(1).replace('\\"', '"').replace("\\\\", "\\")
                    data = json.loads(escaped_json)

                    # Dig into the data (queries[0].state.data is common)
                    job_data = None
                    for query in data.get("queries", []):
                        state = query.get("state", {})
                        q_data = state.get("data", {})
                        if q_data and q_data.get("slug"):
                            job_data = q_data
                            break

                    if job_data:
                        details["title"] = job_data.get("name")
                        details["publication_date"] = job_data.get("published_at")
                        details["description"] = job_data.get(
                            "description"
                        )  # This is HTML, we keep it for dbt to clean if needed or clean here
                        if details["description"]:
                            details["description"] = BeautifulSoup(
                                details["description"], "html.parser"
                            ).get_text(separator="\n", strip=True)

                        # Company
                        org = job_data.get("organization", {})
                        details["company"] = org.get("name")

                        # Office / Location
                        office = job_data.get("office", {})
                        if office:
                            details["city"] = office.get("city")
                            details["region"] = office.get("district") or office.get("state")
                            addr_parts = [
                                details["city"],
                                details["region"],
                                office.get("country_code"),
                            ]
                            details["location"] = ", ".join([p for p in addr_parts if p])

                        # Store raw values for ELT (mapping will happen in dbt)
                        details["remote"] = job_data.get("remote")
                        details["contracts"] = (
                            [job_data.get("contract_type")] if job_data.get("contract_type") else []
                        )

                        # Income
                        salary_min = job_data.get("salary_min")
                        salary_max = job_data.get("salary_max")
                        currency = job_data.get("salary_currency", "EUR")

                        if salary_min or salary_max:
                            if salary_min and salary_max:
                                if salary_min == salary_max:
                                    details["income"] = f"{salary_min} {currency}"
                                else:
                                    details["income"] = f"{salary_min}-{salary_max} {currency}"
                            else:
                                details["income"] = f"{salary_min or salary_max} {currency}"

                        # Experience
                        details["experience_level"] = job_data.get("experience_level")

                        # Contracts (Stored Raw for ELT)
                        ctype = job_data.get("contract_type")
                        if ctype:
                            details["contracts"] = [ctype]

                        return details  # Success
            except Exception as e:
                print(f"Error parsing __INITIAL_DATA__: {e}")

        # 2. Fallback: JSON-LD (what we had before)
        ld_scripts = soup.select('script[type="application/ld+json"]')
        for s in ld_scripts:
            try:
                ld_data = json.loads(s.get_text())
                if isinstance(ld_data, list):
                    ld_data = ld_data[0]
                if ld_data.get("@type") == "JobPosting":
                    details["title"] = details["title"] or ld_data.get("title")
                    details["publication_date"] = details["publication_date"] or ld_data.get(
                        "datePosted"
                    )
                    if not details["company"] and ld_data.get("hiringOrganization"):
                        details["company"] = ld_data["hiringOrganization"].get("name")
                    # ... rest of fallback logic ...
            except Exception:
                pass

    except Exception as e:
        print(f"Error fetching WTTJ details for {url}: {e}")

    return details


def fetch_wttj_jobs(pages: int = 1) -> list[dict]:
    """
    Fetches jobs from WTTJ search using Playwright.
    """
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        stop_scraping = False
        CARD_SELECTOR = 'li[data-testid="search-results-list-item-wrapper"]'

        for p_idx in range(1, pages + 1):
            if stop_scraping:
                break

            url = f"{WTTJ_BASE_URL}&page={p_idx}"
            print(f"Fetching WTTJ page {p_idx}...")

            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_selector(CARD_SELECTOR, timeout=15000)

                job_links_data = page.evaluate("""() => {
                    const cards = Array.from(document.querySelectorAll('li[data-testid="search-results-list-item-wrapper"]'));
                    
                    const parseRelativeDate = (text) => {
                        const now = new Date();
                        const match = text.match(/(\\d+)\\s+(minute|hour|day|month)/i);
                        if (!match) return now.toISOString();
                        const val = parseInt(match[1]);
                        const unit = match[2].toLowerCase();
                        if (unit.includes('minute')) now.setMinutes(now.getMinutes() - val);
                        else if (unit.includes('hour')) now.setHours(now.getHours() - val);
                        else if (unit.includes('day')) now.setDate(now.getDate() - val);
                        else if (unit.includes('month')) now.setMonth(now.getMonth() - val);
                        return now.toISOString();
                    };

                    return cards.map(card => {
                        const link = card.querySelector('a[href*="/jobs/"]');
                        const time = card.querySelector('time');
                        return {
                            url: link ? link.href : null,
                            job_id: link ? link.getAttribute('href').split('/').pop() : null,
                            datetime: time?.getAttribute('datetime') || parseRelativeDate(time?.innerText || "")
                        };
                    }).filter(j => j.url);
                }""")

                print(f"Found {len(job_links_data)} link(s)")

                for job_link in job_links_data:
                    full_url = job_link["url"]
                    job_id = job_link["job_id"]

                    # Page 1 date reporting
                    if job_link["datetime"]:
                        pub_date = datetime.fromisoformat(
                            job_link["datetime"].replace("Z", "+00:00")
                        )
                        hours_diff = (
                            datetime.now(pub_date.tzinfo) - pub_date
                        ).total_seconds() / 3600

                        if hours_diff > 24:
                            print(f"Stopping: {job_id} is {hours_diff:.1f}h old (sorted by mostRecent)")
                            stop_scraping = True
                            break
                        else:
                            print(f"Job {job_id} is {hours_diff:.1f}h old - OK")

                    details = fetch_wttj_details(full_url)

                    job_payload = build_wttj_job_payload(
                        job_id=job_id,
                        url=full_url,
                        details=details,
                        publication_date_fallback=job_link["datetime"],
                    )

                    jobs.append(job_payload)
                    time.sleep(random.uniform(0.2, 0.4))

            except Exception as e:
                print(f"Error on page {p_idx}: {e}")
                break

        browser.close()

    return jobs


if __name__ == "__main__":
    print("--- STARTING WTTJ DEEP SCRAPING ---")
    data = fetch_wttj_jobs(pages=1)
    print(f"Fetched {len(data)} total jobs.")

    if data:
        ingest_jobs(data, table_name="RAW_WTTJ")
