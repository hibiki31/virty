from fastapi import HTTPException

def notfound_exception(msg):
    return HTTPException(
        status_code=404,
        detail=msg
    )
