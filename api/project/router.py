from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from domain.models import DomainModel
from flavor.models import FlavorModel
from mixin.database import get_db
from mixin.exception import ApiError, ApiErrorCode
from mixin.log import setup_logger
from network.models import NetworkPoolModel
from resource_authorization import require_admin
from storage.models import StoragePoolModel
from user.models import UserModel

from .models import ProjectModel
from .schemas import (
    ProjectDetail,
    ProjectForNameUpdate,
    ProjectForQuery,
    ProjectLimits,
    ProjectMember,
    ProjectMemberForQuery,
    ProjectMemberPage,
    ProjectPage,
    ProjectResourceGrantCandidates,
    ProjectResourceGrantsUpdate,
    ProjectResourceReference,
    ProjectSummary,
)
from .service import (
    ProjectConflictError,
    ProjectGrantNotFoundError,
    ProjectMemberNotFoundError,
    ProjectNotFoundError,
    add_project_member as add_member,
    lock_project,
    remove_project_member as remove_member,
    rename_project,
    replace_project_resource_grants,
)

app = APIRouter(prefix="/api/projects", tags=["projects"])
logger = setup_logger(__name__)


def _get_member_project(
    db: Session,
    project_id: str,
    current_user: CurrentUser,
    *,
    lock: bool = False,
) -> ProjectModel:
    project: ProjectModel | None
    if lock:
        try:
            project = lock_project(db, project_id)
        except ProjectNotFoundError:
            raise ApiError(
                status.HTTP_404_NOT_FOUND,
                ApiErrorCode.PROJECT_NOT_FOUND,
                "The project was not found.",
            ) from None
    else:
        project = db.get(ProjectModel, project_id)
    if project is None or project_id not in current_user.projects:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            ApiErrorCode.PROJECT_NOT_FOUND,
            "The project was not found.",
        )
    return project


def _get_usage(
    db: Session,
    project_ids: list[str],
) -> dict[str, tuple[int, float, int]]:
    if not project_ids:
        return {}
    rows = (
        db.query(
            DomainModel.owner_project_id,
            func.coalesce(func.sum(DomainModel.core), 0),
            func.coalesce(func.sum(DomainModel.memory), 0),
            func.coalesce(func.sum(DomainModel.storage_used), 0),
        )
        .filter(DomainModel.owner_project_id.in_(project_ids))
        .group_by(DomainModel.owner_project_id)
        .all()
    )
    return {
        str(project_id): (
            int(used_core),
            float(used_memory) / 1024,
            int(used_storage),
        )
        for project_id, used_core, used_memory, used_storage in rows
    }


def _summary(
    project: ProjectModel,
    usage: tuple[int, float, int] = (0, 0, 0),
) -> ProjectSummary:
    return ProjectSummary(
        id=project.id,
        name=project.name,
        member_count=len(project.users),
        used_core=usage[0],
        used_memory_g=usage[1],
        used_storage_g=usage[2],
    )


def _detail(db: Session, project: ProjectModel) -> ProjectDetail:
    usage = _get_usage(db, [project.id]).get(project.id, (0, 0, 0))
    summary = _summary(project, usage)
    return ProjectDetail(
        **summary.model_dump(),
        limits=ProjectLimits(
            core=project.core,
            memory_g=project.memory_g,
            storage_capacity_g=project.storage_capacity_g,
            enforced=False,
        ),
        members=[
            ProjectMember(username=user.username)
            for user in sorted(project.users, key=lambda user: user.username)
        ],
        resource_grants=ProjectResourceGrantsUpdate(
            storage_pool_ids=sorted(pool.id for pool in project.storage_pools),
            network_pool_ids=sorted(pool.id for pool in project.network_pools),
            flavor_ids=sorted(flavor.id for flavor in project.flavors),
        ),
        storage_pools=[
            ProjectResourceReference(id=pool.id, name=pool.name or f"Pool {pool.id}")
            for pool in sorted(project.storage_pools, key=lambda pool: pool.id)
        ],
        network_pools=[
            ProjectResourceReference(id=pool.id, name=pool.name or f"Pool {pool.id}")
            for pool in sorted(project.network_pools, key=lambda pool: pool.id)
        ],
        flavors=[
            ProjectResourceReference(id=flavor.id, name=flavor.name)
            for flavor in sorted(project.flavors, key=lambda flavor: flavor.id)
        ],
    )


def _raise_service_error(
    error: ValueError,
    *,
    conflict_code: ApiErrorCode,
    conflict_message: str,
) -> None:
    if isinstance(error, ProjectMemberNotFoundError):
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            ApiErrorCode.PROJECT_MEMBER_NOT_FOUND,
            "The project member was not found.",
        ) from error
    if isinstance(error, ProjectGrantNotFoundError):
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            ApiErrorCode.PROJECT_GRANT_NOT_FOUND,
            "A project grant resource was not found.",
        ) from error
    raise ApiError(
        status.HTTP_409_CONFLICT,
        conflict_code,
        conflict_message,
    ) from error


@app.get("", response_model=ProjectPage)
def get_projects(
    param: ProjectForQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProjectPage:
    current_user.verify_scope(["project.read"])
    query = db.query(ProjectModel).filter(
        ProjectModel.id.in_(current_user.projects),
    )
    if param.name_like:
        query = query.filter(ProjectModel.name.like(f"%{param.name_like}%"))

    count = query.count()
    query = query.order_by(ProjectModel.name, ProjectModel.id)
    if param.limit > 0:
        query = query.limit(param.limit).offset(param.limit * param.page)
    projects = query.all()
    usage = _get_usage(db, [project.id for project in projects])
    return ProjectPage(
        count=count,
        data=[_summary(project, usage.get(project.id, (0, 0, 0))) for project in projects],
    )


@app.get("/{project_id}", response_model=ProjectDetail)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProjectDetail:
    current_user.verify_scope(["project.read"])
    return _detail(db, _get_member_project(db, project_id, current_user))


@app.patch("/{project_id}", response_model=ProjectDetail)
def update_project_name(
    project_id: str,
    request: ProjectForNameUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProjectDetail:
    current_user.verify_scope(["project.manage"])
    project = _get_member_project(db, project_id, current_user, lock=True)
    try:
        rename_project(project, request.name)
    except ProjectConflictError as error:
        _raise_service_error(
            error,
            conflict_code=ApiErrorCode.PROJECT_UPDATE_CONFLICT,
            conflict_message="The project could not be updated.",
        )
    db.commit()
    return _detail(db, project)


@app.put("/{project_id}/members/{username}", response_model=ProjectDetail)
def add_project_member(
    project_id: str,
    username: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProjectDetail:
    current_user.verify_scope(["project.manage"])
    project = _get_member_project(db, project_id, current_user, lock=True)
    try:
        add_member(db, project, username)
    except ProjectMemberNotFoundError as error:
        _raise_service_error(
            error,
            conflict_code=ApiErrorCode.PROJECT_MEMBER_CONFLICT,
            conflict_message="The project membership could not be updated.",
        )
    db.commit()
    return _detail(db, project)


@app.delete("/{project_id}/members/{username}", response_model=ProjectDetail)
def remove_project_member(
    project_id: str,
    username: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProjectDetail:
    current_user.verify_scope(["project.manage"])
    project = _get_member_project(db, project_id, current_user, lock=True)
    try:
        remove_member(project, username)
    except ProjectConflictError as error:
        _raise_service_error(
            error,
            conflict_code=ApiErrorCode.PROJECT_MEMBER_CONFLICT,
            conflict_message="The project membership could not be updated.",
        )
    db.commit()
    return _detail(db, project)


@app.get(
    "/{project_id}/member-candidates",
    response_model=ProjectMemberPage,
)
def get_project_member_candidates(
    project_id: str,
    param: ProjectMemberForQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProjectMemberPage:
    current_user.verify_scope(["project.manage"])
    project = _get_member_project(db, project_id, current_user)
    member_ids = [member.username for member in project.users]
    query = db.query(UserModel).filter(UserModel.username.notin_(member_ids))
    if param.name_like:
        query = query.filter(UserModel.username.like(f"%{param.name_like}%"))
    count = query.count()
    query = query.order_by(UserModel.username)
    if param.limit > 0:
        query = query.limit(param.limit).offset(param.limit * param.page)
    return ProjectMemberPage(
        count=count,
        data=[ProjectMember(username=user.username) for user in query.all()],
    )


@app.put("/{project_id}/resource-grants", response_model=ProjectDetail)
def update_project_resource_grants(
    project_id: str,
    request: ProjectResourceGrantsUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProjectDetail:
    current_user.verify_scope(["project.manage"])
    require_admin(current_user)
    try:
        project = lock_project(db, project_id)
    except ProjectNotFoundError:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            ApiErrorCode.PROJECT_NOT_FOUND,
            "The project was not found.",
        ) from None
    try:
        replace_project_resource_grants(db, project, request)
    except (ProjectConflictError, ProjectGrantNotFoundError) as error:
        _raise_service_error(
            error,
            conflict_code=ApiErrorCode.PROJECT_GRANT_CONFLICT,
            conflict_message="The project resource grants could not be updated.",
        )
    db.commit()
    return _detail(db, project)


@app.get(
    "/{project_id}/resource-grant-candidates",
    response_model=ProjectResourceGrantCandidates,
)
def get_project_resource_grant_candidates(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ProjectResourceGrantCandidates:
    """global admin向けにProjectへ割当可能なresourceを列挙する。"""

    current_user.verify_scope(["project.manage"])
    require_admin(current_user)
    if db.get(ProjectModel, project_id) is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            ApiErrorCode.PROJECT_NOT_FOUND,
            "The project was not found.",
        )
    return ProjectResourceGrantCandidates(
        storage_pools=[
            ProjectResourceReference(id=pool.id, name=pool.name or f"Pool {pool.id}")
            for pool in db.query(StoragePoolModel).order_by(StoragePoolModel.id)
        ],
        network_pools=[
            ProjectResourceReference(id=pool.id, name=pool.name or f"Pool {pool.id}")
            for pool in db.query(NetworkPoolModel).order_by(NetworkPoolModel.id)
        ],
        flavors=[
            ProjectResourceReference(id=flavor.id, name=flavor.name)
            for flavor in db.query(FlavorModel).order_by(FlavorModel.id)
        ],
    )
