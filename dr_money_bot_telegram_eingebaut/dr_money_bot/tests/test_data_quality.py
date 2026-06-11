from app.core.models import Lead
from app.storage.json_repository import JsonRepository


def test_duplicate_merge_by_domain(tmp_path):
    repo = JsonRepository(str(tmp_path))
    first = repo.upsert_lead(Lead(company_name='ABC Wind GmbH', website='https://www.abc-wind.ch', country='Schweiz'))
    second = repo.upsert_lead(Lead(company_name='ABC Wind AG', website='abc-wind.ch', phone='+41 41 123 45 67', ceo='Max Muster', country='Schweiz'))
    leads = repo.list_leads()
    assert first.action == 'created'
    assert second.action == 'merged_duplicate'
    assert len(leads) == 1
    assert leads[0].ceo == 'Max Muster'
    assert leads[0].phone == '+41411234567'


def test_quality_score_core_fields(tmp_path):
    repo = JsonRepository(str(tmp_path))
    result = repo.upsert_lead(Lead(company_name='Solar Projekt AG', website='solar.example.com', country='Deutschland', activity='Solarpark'))
    assert result.lead.quality_score >= 45
    assert result.lead.duplicate_key.startswith('domain:')
