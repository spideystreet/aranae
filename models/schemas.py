from pydantic import BaseModel


class JobSchema(BaseModel):
    job_id: str
    title: str | None = None
    company: str | None = None
    publication_date: str | None = None
    location: str | None = None
    city: str | None = None
    region: str | None = None
    income: str | None = None
    skills: list[str] | str | None = None
    contracts: list[str] | str | None = None
    duration: str | None = None
    experience_level: str | None = None
    start_date: str | None = None
    url: str | None = None
    source: str | None = None
    description: str | None = None
    remote: str | None = None

    def to_db_dict(self):
        """Converts the model to a dictionary suitable for database insertion."""
        data = self.model_dump()
        # Convert list fields to comma-separated strings for PostgreSQL
        if isinstance(data.get("contracts"), list):
            data["contracts"] = ", ".join(data["contracts"])
        if isinstance(data.get("skills"), list):
            data["skills"] = ", ".join(data["skills"])
        return data
