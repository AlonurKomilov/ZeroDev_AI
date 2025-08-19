from typing import List

from fastapi import APIRouter

from backend.services.template_service import Template, template_service

router = APIRouter()


@router.get("/", response_model=List[Template])
def list_templates():
    """
    Get a list of all available project templates.
    """
    return template_service.get_all_templates()
