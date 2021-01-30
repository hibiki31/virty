from fastapi import HTTPException

exception_notfund = HTTPException(
    status_code=404,
    detail="Object not fund."
)