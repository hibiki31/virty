
from fastapi import HTTPException, status
from sqlalchemy.orm.exc import NoResultFound


def raise_notfound(detail: str = "The specified resource was not found."):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )

def raise_forbidden(detail: str = "You do not have permission to perform this action.") -> None:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


NoResultFound