from backend.agents.codegen_agent import extract_name_from_spec
from backend.models.spec_model import ProjectSpec

def test_extract_name_from_spec():
    spec = ProjectSpec(
        name="Awesome AI CRM",
        description="CRM for leads and clients",
        language="python",
        features=[]
    )
    result = extract_name_from_spec(spec)
    assert result == "awesome_ai_crm"
