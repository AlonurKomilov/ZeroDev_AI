import json
from pathlib import Path
from pydantic import BaseModel
from typing import List

class Template(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]

class TemplateService:
    def __init__(self, templates_file: Path):
        self.templates_file = templates_file
        self.templates = self._load_templates()

    def _load_templates(self) -> List[Template]:
        with open(self.templates_file, "r") as f:
            templates_data = json.load(f)
        return [Template(**t) for t in templates_data]

    def get_all_templates(self) -> List[Template]:
        return self.templates

# Assuming the templates.json file is in the same directory as the main app
templates_path = Path(__file__).parent.parent / "templates.json"
template_service = TemplateService(templates_path)
