from sqlalchemy.orm import Session

from models import UserModel, UserScopeModel


def overwrite_user_scopes(
    db: Session,
    user: UserModel,
    new_scope_names: list[str],
) -> None:
    """users_scope を new_scope_names の内容で完全に置き換える"""
    new_scope_set = set(new_scope_names)
    existing = {s.name: s for s in user.scopes}

    for obsolete_name in existing.keys() - new_scope_set:
        db.delete(existing[obsolete_name])

    for missing_name in new_scope_set - existing.keys():
        user.scopes.append(UserScopeModel(name=missing_name))
