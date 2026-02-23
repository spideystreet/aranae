from services.transformers import build_freework_job_payload, build_wttj_job_payload

FREEWORK_DETAILS = {
    "title": "Développeur Python",
    "company": "Acme",
    "publication_date": "2026-02-01",
    "location": "Paris, Île-de-France, FR",
    "city": "Paris",
    "region": "Île-de-France",
    "income": "500 € / j",
    "duration": "6 mois",
    "experience_level": "5 ans",
    "start_date": "ASAP",
    "remote": "Télétravail 100%",
    "description": "Une belle mission.",
}

WTTJ_DETAILS = {
    "title": "Data Engineer",
    "company": "Corp",
    "publication_date": "2026-02-10",
    "location": "Lyon, FR",
    "city": "Lyon",
    "region": "Auvergne-Rhône-Alpes",
    "income": "50K-60K €/an",
    "skills": ["Spark", "dbt"],
    "contracts": ["full_time"],
    "duration": None,
    "experience_level": "3 à 5 ans d'expérience",
    "start_date": None,
    "remote": "partial",
    "description": "Poste en CDI.",
}


class TestBuildFreeworkPayload:
    def test_source_is_free_work(self):
        payload = build_freework_job_payload(
            "fw-001", "https://example.com", FREEWORK_DETAILS, [], []
        )
        assert payload["source"] == "free-work"

    def test_job_id_and_url(self):
        payload = build_freework_job_payload(
            "fw-001", "https://example.com", FREEWORK_DETAILS, [], []
        )
        assert payload["job_id"] == "fw-001"
        assert payload["url"] == "https://example.com"

    def test_details_mapped_correctly(self):
        payload = build_freework_job_payload(
            "fw-001", "https://example.com", FREEWORK_DETAILS, ["Freelance"], ["Python"]
        )
        assert payload["title"] == "Développeur Python"
        assert payload["city"] == "Paris"
        assert payload["contracts"] == ["Freelance"]
        assert payload["skills"] == ["Python"]

    def test_publication_date_fallback(self):
        details = {**FREEWORK_DETAILS, "publication_date": None}
        payload = build_freework_job_payload(
            "fw-001", "https://example.com", details, [], [], publication_date_fallback="01/02/2026"
        )
        assert payload["publication_date"] == "01/02/2026"

    def test_publication_date_detail_takes_priority(self):
        payload = build_freework_job_payload(
            "fw-001",
            "https://example.com",
            FREEWORK_DETAILS,
            [],
            [],
            publication_date_fallback="01/01/2000",
        )
        assert payload["publication_date"] == "2026-02-01"

    def test_all_keys_present(self):
        payload = build_freework_job_payload(
            "fw-001", "https://example.com", FREEWORK_DETAILS, [], []
        )
        expected_keys = {
            "job_id",
            "title",
            "company",
            "publication_date",
            "contracts",
            "skills",
            "duration",
            "experience_level",
            "income",
            "location",
            "city",
            "region",
            "description",
            "start_date",
            "remote",
            "url",
            "source",
        }
        assert expected_keys == set(payload.keys())


class TestBuildWttjPayload:
    def test_source_is_wttj(self):
        payload = build_wttj_job_payload("wttj-001", "https://example.com", WTTJ_DETAILS)
        assert payload["source"] == "wttj"

    def test_details_mapped_correctly(self):
        payload = build_wttj_job_payload("wttj-001", "https://example.com", WTTJ_DETAILS)
        assert payload["title"] == "Data Engineer"
        assert payload["city"] == "Lyon"
        assert payload["skills"] == ["Spark", "dbt"]
        assert payload["contracts"] == ["full_time"]

    def test_publication_date_fallback(self):
        details = {**WTTJ_DETAILS, "publication_date": None}
        payload = build_wttj_job_payload(
            "wttj-001",
            "https://example.com",
            details,
            publication_date_fallback="2026-02-10T10:00:00Z",
        )
        assert payload["publication_date"] == "2026-02-10T10:00:00Z"

    def test_skills_defaults_to_empty_list(self):
        details = {**WTTJ_DETAILS, "skills": None}
        payload = build_wttj_job_payload("wttj-001", "https://example.com", details)
        assert payload["skills"] == []

    def test_all_keys_present(self):
        payload = build_wttj_job_payload("wttj-001", "https://example.com", WTTJ_DETAILS)
        expected_keys = {
            "job_id",
            "title",
            "company",
            "publication_date",
            "contracts",
            "skills",
            "duration",
            "experience_level",
            "income",
            "location",
            "city",
            "region",
            "description",
            "start_date",
            "remote",
            "url",
            "source",
        }
        assert expected_keys == set(payload.keys())
