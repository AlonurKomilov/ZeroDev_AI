import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.core.database import get_session
from backend.core.security import current_active_user
from backend.models.project_model import Project
from backend.models.user_model import User
from backend.schemas.project_schemas import ProjectCreate, ProjectRead, ProjectUpdate
from backend.tasks.project_tasks import (
    create_project_files_task,
    delete_project_files_task,
)

router = APIRouter()


@router.post("/", response_model=ProjectRead, status_code=201)
def create_project(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(current_active_user),
    project_in: ProjectCreate,
):
    """
    Create a new project for the current user.
    """
    project = Project.from_orm(project_in, update={"user_id": current_user.id})
    session.add(project)
    session.commit()
    session.refresh(project)

    # Dispatch background task to create project files
    create_project_files_task.delay(str(current_user.id), str(project.id))

    return project


@router.get("/", response_model=list[ProjectRead])
def read_projects(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve all projects for the current user.
    """
    projects = session.exec(
        select(Project)
        .where(Project.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def read_project(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(current_active_user),
    project_id: uuid.UUID,
):
    """
    Get a specific project by ID.
    """
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )
    return project


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(current_active_user),
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
):
    """
    Update a project.
    """
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )

    project_data = project_in.dict(exclude_unset=True)
    for key, value in project_data.items():
        setattr(project, key, value)

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(current_active_user),
    project_id: uuid.UUID,
):
    """
    Delete a project.
    """
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )

    # Dispatch background task to delete project files
    delete_project_files_task.delay(str(current_user.id), str(project.id))

    session.delete(project)
    session.commit()
    return {"ok": True}
