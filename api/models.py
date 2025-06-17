from domain.models import DomainDriveModel, DomainInterfaceModel, DomainModel
from flavor.models import FlavorModel
from network.models import NetworkModel
from node.models import NodeModel, NodeRoleModel
from project.models import ProjectModel
from task.models import TaskModel
from user.models import UserModel, UserScopeModel


def orm_initializing_mappler():
    UserModel, UserScopeModel
    DomainDriveModel, DomainInterfaceModel, DomainModel
    NodeModel, NodeRoleModel

    TaskModel
    NetworkModel
    FlavorModel
    ProjectModel