from typing import Dict, List, Optional, Any

def build_freework_job_payload(
    job_id: str,
    url: str,
    details: Dict,
    contracts: List[str],
    skills: List[str],
    publication_date_fallback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Constructs the standardized job dictionary for Free-Work.
    """
    return {
        "job_id": job_id,
        "title": details.get('title'),
        "company": details.get('company'),
        "publication_date": details.get('publication_date') or publication_date_fallback,
        "contracts": contracts,
        "skills": skills,
        "duration": details.get('duration'),
        "experience_level": details.get('experience_level'),
        "income": details.get('income'),
        "location": details.get('location'),
        "city": details.get('city'),
        "region": details.get('region'),
        "description": details.get('description'),
        "start_date": details.get('start_date'),
        "remote": details.get('remote'),
        "url": url,
        "source": "free-work"
    }

def build_wttj_job_payload(
    job_id: str,
    url: str,
    details: Dict,
    publication_date_fallback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Constructs the standardized job dictionary for Welcome to the Jungle.
    """
    return {
        "job_id": job_id,
        "title": details.get('title'),
        "company": details.get('company'),
        "publication_date": details.get('publication_date') or publication_date_fallback,
        "location": details.get('location'),
        "city": details.get('city'),
        "region": details.get('region'),
        "income": details.get('income'),
        "skills": details.get('skills', []),
        "contracts": details.get('contracts', []),
        "duration": details.get('duration'),
        "experience_level": details.get('experience_level'),
        "start_date": details.get('start_date'),
        "remote": details.get('remote'),
        "description": details.get('description'),
        "url": url,
        "source": "wttj"
    }
