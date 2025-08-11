from fastapi import APIRouter, Depends
from typing import List

from backend.services.template_service import template_service, Template

router = APIRouter()

@router.get("/", response_model=List[Template])
def list_templates():
    """
    Get a list of all available project templates.
    """
    return template_service.get_all_templates()
