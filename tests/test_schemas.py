import pytest
from pydantic import ValidationError

from models.schemas import JobSchema


def test_valid_minimal():
    job = JobSchema(job_id="abc123")
    assert job.job_id == "abc123"
    assert job.title is None


def test_valid_full():
    job = JobSchema(
        job_id="fw-001",
        title="Développeur Python",
        company="Acme",
        publication_date="2026-02-01",
        location="Paris, Île-de-France, FR",
        city="Paris",
        region="Île-de-France",
        income="500 € / j",
        skills=["Python", "Django"],
        contracts=["Freelance"],
        duration="6 mois",
        experience_level="5 ans d'expérience",
        start_date="ASAP",
        url="https://free-work.com/job/fw-001",
        source="free-work",
        description="Une belle mission.",
        remote="Télétravail 100%",
    )
    assert job.title == "Développeur Python"
    assert job.source == "free-work"


def test_missing_job_id_raises():
    with pytest.raises(ValidationError):
        JobSchema()


def test_to_db_dict_converts_lists():
    job = JobSchema(
        job_id="fw-002",
        skills=["Python", "FastAPI"],
        contracts=["CDI", "Freelance"],
    )
    db = job.to_db_dict()
    assert db["skills"] == "Python, FastAPI"
    assert db["contracts"] == "CDI, Freelance"


def test_to_db_dict_keeps_strings():
    job = JobSchema(job_id="fw-003", skills="Python", contracts="CDI")
    db = job.to_db_dict()
    assert db["skills"] == "Python"
    assert db["contracts"] == "CDI"


def test_to_db_dict_handles_none():
    job = JobSchema(job_id="fw-004")
    db = job.to_db_dict()
    assert db["skills"] is None
    assert db["contracts"] is None
