from fastapi import HTTPException, status

def notfound_exception(msg):
    return HTTPException(
        status_code=404,
        detail=msg
    )

def instance_already_exists(msg):
    return HTTPException(
        status_code=403,
        detail=msg
    )
    
class AlreadyExists(HTTPException):
    def __init__(self, detail: str = "Already exists"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class NotFound(HTTPException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    