from pydantic import BaseModel, Field
from typing import List, Optional, Union

class JobSchema(BaseModel):
    job_id: str
    title: Optional[str] = None
    company: Optional[str] = None
    publication_date: Optional[str] = None
    location: Optional[str] = None
    income: Optional[str] = None
    skills: Optional[Union[List[str], str]] = None
    contracts: Optional[Union[List[str], str]] = None
    duration: Optional[str] = None
    experience_level: Optional[str] = None
    start_date: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None

    def to_db_dict(self):
        """Converts the model to a dictionary suitable for database insertion."""
        data = self.model_dump()
        # Convert list fields to comma-separated strings for PostgreSQL
        if isinstance(data.get('contracts'), list):
            data['contracts'] = ', '.join(data['contracts'])
        if isinstance(data.get('skills'), list):
            data['skills'] = ', '.join(data['skills'])
        return data
