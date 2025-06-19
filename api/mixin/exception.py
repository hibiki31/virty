from fastapi import HTTPException
from sqlalchemy.orm.exc import NoResultFound


def notfound_exception(msg):
    return HTTPException(
        status_code=404,
        detail=msg
    )

NoResultFound