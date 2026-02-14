
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from typing import List, Dict, Optional
import time
import random

BASE_URL = "https://www.free-work.com/fr/tech-it/jobs"
CUSTOM_URL = "https://www.free-work.com/fr/tech-it/jobs?query=&locations=fr~~~&contracts=contractor&contracts=permanent&contracts=apprenticeship&contracts=internship&contracts=fixed-term&freshness=less_than_24_hours"

def fetch_details(url: str) -> Dict:
    """
    Fetches the full details from the job detail page.
    Returns a dict with location, salary, tjm, duration, description, etc.
    """
    details = {
        'location': None,
        'income': None, # Consolidated salary/tjm
        'duration': None,
        'experience_level': None, # New field
        'company': None,
        'description': None,
        'start_date': None
    }
    
    try:
        if not url or url == "N/A": return details
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return details
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- JSON-LD Extraction (Priority 1) ---
        ld_scripts = soup.select('script[type="application/ld+json"]')
        for s in ld_scripts:
            try:
                data = json.loads(s.get_text())
                if data.get('@type') == 'JobPosting':
                    # Extract cleanly
                    if data.get('hiringOrganization'):
                        details['company'] = data['hiringOrganization'].get('name')
                    
                    if data.get('jobLocation'):
                        addr = data['jobLocation'].get('address', {})
                        if isinstance(addr, dict):
                            # Construct location string: City, Region, Country
                            parts = [addr.get('addressLocality'), addr.get('addressRegion'), addr.get('addressCountry')]
                            details['location'] = ', '.join([p for p in parts if p])
                    
                    if data.get('description'):
                        # It is HTML, so strip it or keep it? User wants clean text usually.
                        # But scraper.py usually returns text.
                        # Let's use BS4 to strip HTML from it
                        details['description'] = BeautifulSoup(data['description'], 'html.parser').get_text(separator="\n", strip=True)
                    
                    if data.get('datePosted'):
                        # We can use this to override list date if needed, but list date is fine.
                        pass
                    
                    break # Found the JobPosting
            except:
                pass

            except:
                pass
        
        if not details['company']:
             # Small safety net: if JSON-LD entirely failed to parse or missing type
             # We might leave it None, as user requested "ONLY JSON-LD".
             # But if user says "uniquement le json-ld sur chaque offre pour les matadatas",
             # it implies "don't mix sources".
             pass

        # --- Grid Section (Salary, TJM, Duration) ---
        # User snippet: <div class="grid"> ... <div class="flex items-center py-1"> <span ...> Text </span> </div> ... </div>
        # We look for the grid container and iterate its items
        grid_div = soup.select_one('div.grid')
        if grid_div:
            # Iterate over all items in the grid
            items = grid_div.select('div.flex.items-center.py-1 span.w-full.text-sm.line-clamp-2')
            for span in items:
                text = span.get_text(strip=True)
                # Normalize text: fraction slash to slash, nbsp to space
                text_clean = text.replace('\u2044', '/').replace('\xa0', ' ')
                lower_text = text_clean.lower()
                
                # Logic per user rules:
                # Capture all monetary values into 'income'
                if '€' in lower_text or 'k€' in lower_text or 'eur' in lower_text:
                     details['income'] = text_clean
                
                if 'mois' in lower_text or 'ans' in lower_text or 'semaines' in lower_text or 'durée' in lower_text:
                     # Check if it is "Expérience"
                     if 'expérience' in lower_text:
                         details['experience_level'] = text
                     else:
                         # Otherwise assume duration (e.g. 12 mois)
                         details['duration'] = text
                
                if 'dès que possible' in lower_text or '/' in text and len(text) < 12 and any(c.isdigit() for c in text):
                     # Potential start date
                     details['start_date'] = text

        # --- Description (HTML Fallback) ---
        # User requested JSON-LD only for metadata, so we rely on that.
        # But if JSON-LD missing, description is None.
        # Is this acceptable? Yes ("avoid data errors").
        pass
            
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
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
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
    
    # Selecting job cards strategy 4: Locate by Title Header
    # We found that finding the container is brittle, but finding the title span is robust (35 found).
    # We will extract data relative to the h3 > span structure.
    
    
    title_spans = soup.find_all('span', class_='fw-text-highlight')
    
    jobs = []
    
    for i, span in enumerate(title_spans):
        try:
            # Check if parent is a link to a job
            link_tag = span.find_parent('a')
            
            # If no parent link, or link doesn't look like a job, skip
            if not link_tag:
                 continue
            
            href = link_tag.get('href', '')
            if '/job-mission/' not in href:
                 continue

            # This is a job title!
            title = span.get_text(strip=True)
            full_url = f"https://www.free-work.com{href}"
            
            # Generate a unique ID for deduplication
            job_id = href.split('/')[-1] if href else f"unknown-{i}"

            content_div = link_tag.find_parent('div')
            header_tag = link_tag.find_parent('header')

            if not content_div and not header_tag:
                 continue

            # Re-locate content_div for other details if strictly needed, or just search relative to current position
            if not content_div:
                 content_div = header_tag.parent if header_tag else link_tag.parent.parent

            # Date exists in <time> tag in the list
            date_tag = content_div.select_one('time')
            date_posted = date_tag.get_text(strip=True) if date_tag else None
            
            # --- Fetch Details from Detail Page ---
            # This is where we get the rich info (Company, Salary, TJM, Duration, Location)
            # We do this synchronously, so it might take time.
            details = fetch_details(full_url)
            
            # Merge logic
            company = details.get('company')
            location = details.get('location')
            income = details.get('income')
            duration = details.get('duration')
            experience_level = details.get('experience_level')
            description = details.get('description')
            
            # Fallback for company/location if not found in detail (try list)
            if not company and header_tag:
                 # Try sibling of header in list view
                 next_div = header_tag.find_next_sibling('div')
                 if next_div:
                      company_div = next_div.select_one('.text-base.font-medium.truncate.w-full')
                      if company_div:
                          company = company_div.get_text(strip=True)

            # --- Tag Extraction & Classification ---
            # Extract all potential tags from list view
            # .tag usually contains contracts AND skills on this site
            # .fw-text-highlight are usually skills
            
            raw_tags = set()
            
            # Selector 1: Standard tags
            for t in content_div.select('.tag'):
                raw_tags.add(t.get_text(strip=True))
                
            # Selector 2: Highlighted skills
            for t in content_div.select('[class*="bg-brand-"] .fw-text-highlight'):
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
                "date_posted": date_posted,
                "contracts": contracts,
                "skills": skills,
                "duration": duration,
                "experience_level": experience_level,
                "income": income,
                "location": location,
                "description": description,
                "url": full_url,
                "source": "free-work"
            })
            
            # Polite delay
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error parsing job item {i}: {e}")
            continue
            
    return jobs

if __name__ == "__main__":
    # Test with custom URL
    print(f"Testing scraper with CUSTOM_URL: {CUSTOM_URL}")
    data = fetch_jobs(1, CUSTOM_URL)
    print(f"Fetched {len(data)} jobs.")
    if data:
        for i, job in enumerate(data[:5]):
            print(f"Job {i}:")
            print(f"  Title: {job['title']}")
            print(f"  Company: {job['company']}")
            print(f"  Location: {job['location']}")
            print(f"  Date: {job['date_posted']}")
            print(f"  Contracts: {job['contracts']}")
            print(f"  Income: {job['income']} | Duration: {job['duration']} | XP: {job['experience_level']}")
            print("---")
