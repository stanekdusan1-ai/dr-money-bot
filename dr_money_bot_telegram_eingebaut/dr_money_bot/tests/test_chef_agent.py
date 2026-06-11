from app.agents.chef_agent import ChefAgent
from app.storage.json_repository import JsonRepository


def test_run_search_creates_leads(tmp_path):
    agent = ChefAgent(JsonRepository(str(tmp_path)))
    result = agent.run_search('windräder spanien projektfinanzierung', limit_per_agent=1)
    assert result.payload['created'] >= 1
    assert 'Neue Leads' in result.message
