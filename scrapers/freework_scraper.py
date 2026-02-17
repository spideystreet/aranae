import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from typing import List, Dict, Optional
import time
import random
from services.ingestor import ingest_jobs
from scrapers.utils import get_headers, polite_sleep, extract_json_ld, init_job_details

BASE_URL = "https://www.free-work.com/fr/tech-it/jobs"
CUSTOM_URL = "https://www.free-work.com/fr/tech-it/jobs?query=&locations=fr~~~&contracts=contractor&contracts=permanent&contracts=apprenticeship&contracts=internship&contracts=fixed-term&freshness=less_than_24_hours"

def fetch_details(url: str) -> Dict:
    """
    Fetches the full details from the job detail page.
    Returns a dict with location, salary, tjm, duration, description, etc.
    """
    details = init_job_details()
    
    try:
        if not url or url == "N/A": return details
        
        response = requests.get(url, headers=get_headers(), timeout=10)
        if response.status_code != 200:
            return details
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- JSON-LD Extraction (Priority 1) ---
        ld_data = extract_json_ld(soup)
        if ld_data:
            if ld_data.get('hiringOrganization'):
                details['company'] = ld_data['hiringOrganization'].get('name')
            
            if ld_data.get('jobLocation'):
                addr = ld_data['jobLocation'].get('address', {})
                if isinstance(addr, dict):
                    details['city'] = addr.get('addressLocality')
                    details['region'] = addr.get('addressRegion')
                    country = addr.get('addressCountry')
                    parts = [details['city'], details['region'], country]
                    details['location'] = ', '.join([p for p in parts if p])
            
            if ld_data.get('description'):
                details['description'] = BeautifulSoup(ld_data['description'], 'html.parser').get_text(separator="\n", strip=True)
            
            details['title'] = ld_data.get('title')
            details['publication_date'] = ld_data.get('datePosted')

        # --- Grid Section (Salary, TJM, Duration, Experience) ---
        grid_items = soup.select('div.grid div.flex.items-center.py-1')
        
        for item in grid_items:
            span = item.select_one('span.w-full.text-sm.line-clamp-2')
            if not span:
                continue
                
            text = span.get_text(strip=True).replace('\u2044', '/').replace('\xa0', ' ')
            text_lower = text.lower()
            
            # 1. Income (already robust)
            if any(x in text_lower for x in ['€', 'eur', 'k€']):
                details['income'] = text
                continue
                
            # 2. Experience Level
            # Looking for "expérience" or "exp"
            if 'expér' in text_lower or ' exp' in text_lower or text_lower.startswith('exp'):
                details['experience_level'] = text
                continue
                
            # 3. Start Date
            if 'dès' in text_lower or 'asap' in text_lower:
                details['start_date'] = text
                continue

            # 4. Duration
            # Avoid matching "France" or "Remote" by being stricter.
            # Duration usually contains a number + unit
            units = ['mois', ' an', ' ans', 'semaine', 'durée']
            if any(u in text_lower for u in units) and 'exp' not in text_lower:
                # Extra safety: check if it contains a digit
                if any(char.isdigit() for char in text):
                    details['duration'] = text
                continue
            
            # 5. Remote (Raw storage for ELT)
            if 'télétravail' in text_lower or 'remote' in text_lower:
                 details['remote'] = text
                 continue

        # Fallback/Safety: If JSON-LD failed for title/company/location
        if not details['title']:
            h1 = soup.select_one('h1')
            if h1: details['title'] = h1.get_text(strip=True)
            
        if not details['location']:
             # Last item in grid is usually location if not captured
             if grid_items:
                 last_text = grid_items[-1].get_text(strip=True)
                 if 'france' in last_text.lower() or ',' in last_text:
                     details['location'] = last_text
            
    except Exception as e:
        print(f"Error fetching details for {url}: {e}")
        
    return details

def fetch_jobs(page: int = 1, url: str = BASE_URL) -> List[Dict]:
    """
    Fetches jobs from free-work.com and returns a list of dictionaries.
    If using filters (CUSTOM_URL), page parameter is appended with &page=.
    """
    target_url = f"{url}&page={page}" if '?' in url else f"{url}?page={page}"
    print(f"Fetching {target_url}...")
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page {page}: {e}")
        return []
    
    # Check if we got a valid page content
    if "fw-text-highlight" not in response.text:
        print(f"Warning: 'fw-text-highlight' not found in response text. Content length: {len(response.text)}")
        # Debug: save to file for inspection
        with open(f"debug_page_{page}.html", "w") as f:
            f.write(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Selecting job cards.
    # Based on the dump, job cards are <a> tags with specific styling.
    # However, because of nested <a> tags in the HTML source (which is invalid), 
    # BS4 might close the outer <a> early or restructure the tree.
    # Let's try to find the <h3> with the title first, then find the parent container.
    
    job_containers = []
    
    # Selecting job cards strategy 6: Unique Job Links
    # We find all links to job missions and process them uniquely.
    # We try to find the card container to extract list-level info like date/tags.
    links = soup.select('a[href*="/job-mission/"]')
    processed_urls = set()
    
    jobs = []
    
    for i, link_tag in enumerate(links):
        try:
            href = link_tag.get('href', '')
            if not href or href in processed_urls:
                continue
            processed_urls.add(href)
            
            full_url = f"https://www.free-work.com{href}"
            
            # Generate a unique ID for deduplication
            job_id = href.split('/')[-1] if href else f"unknown-{i}"

            # Try to find the closest card container (usually a div or a with bg-white)
            card = link_tag.find_parent(class_=lambda x: x and 'bg-white' in x)
            if not card:
                 card = link_tag.parent.parent # fallback
            
            # Date exists in <time> tag in the card
            date_tag = card.select_one('time') if card else None
            date_posted = date_tag.get_text(strip=True) if date_tag else None
            
            # --- Fetch Details from Detail Page ---
            details = fetch_details(full_url)
            
            # Merge logic
            # Prioritize detail page title and dates
            title = details.get('title')
            company = details.get('company')
            location = details.get('location')
            city = details.get('city')
            region = details.get('region')
            income = details.get('income')
            duration = details.get('duration')
            experience_level = details.get('experience_level')
            description = details.get('description')
            start_date = details.get('start_date')
            
            # Publication Date: JSON-LD priority, fallback to list view
            publication_date = details.get('publication_date') or date_posted

            # --- Tag Extraction & Classification ---
            # Extract tags from the card container
            raw_tags = set()
            
            if card:
                # Selector 1: Standard tags
                for t in card.select('.tag'):
                    raw_tags.add(t.get_text(strip=True))
                    
                # Selector 2: Highlighted skills
                for t in card.select('[class*="bg-brand-"] .fw-text-highlight'):
                    raw_tags.add(t.get_text(strip=True))
                
            contracts = []
            skills = []
            
            # Whitelist for contracts (Strict User List)
            VALID_CONTRACTS = {
                'freelance', 'cdi', 'cdd', 'alternance', 'stage'
            }
            
            for tag in raw_tags:
                if tag.lower() in VALID_CONTRACTS:
                    contracts.append(tag)
                else:
                    skills.append(tag)
            
            # Add to list
            jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company,
                "publication_date": publication_date,
                "contracts": contracts,
                "skills": skills,
                "duration": duration,
                "experience_level": experience_level,
                "income": income,
                "location": location,
                "city": city,
                "region": region,
                "description": description,
                "start_date": start_date,
                "remote": details.get('remote'),
                "url": full_url,
                "source": "free-work"
            })
            
            # Polite delay
            polite_sleep()
            
        except Exception as e:
            print(f"Error parsing job item {i}: {e}")
            continue
            
    return jobs

if __name__ == "__main__":
    # Ingestion run
    print(f"--- STARTING INGESTION WITH CUSTOM_URL: {CUSTOM_URL} ---")
    data = fetch_jobs(1, CUSTOM_URL)
    print(f"Fetched {len(data)} jobs.")
    
    if data:
        # Ingest into database
        ingest_jobs(data, table_name="RAW_FREEWORK")
        
        # Print first few for confirmation
        for i, job in enumerate(data[:5]):
            print(f"Job {i}:")
            print(f"  Title: {job['title']}")
            print(f"  Company: {job['company']}")
            print(f"  Location: {job['location']}")
            print(f"  Date: {job['publication_date']}")
            print(f"  Contracts: {job['contracts']}")
            print(f"  Income: {job['income']} | Duration: {job['duration']} | XP: {job['experience_level']}")
            print("---")
