from typing import List

from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse

import repository.requests as requests_db
import repository.schedule as schedules_db
import repository.operators as operators_db
from api import router
from models.models import Request

"""
db integrity:
- schedule delete - delete all schedule's requests
- operator delete - delete all operator's requests
- add availability - check for no duplications - NOT CHECKING
"""


@router.get("/requests/", response_model=List[Request])
def get_requests(schedule_id: str = Query(None), operator_id: str = Query(None)):
    result = requests_db.get_requests(schedule_id, operator_id)
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No requests found")


@router.post("/requests/create/")
def add_request(request: Request):
    schedule_exists = schedules_db.get_schedule(request.schedule_id)
    operator_exists = operators_db.get_operator(request.operator_id)
    if schedule_exists and operator_exists:
        result = requests_db.add_request(request)
        if result.inserted_id:
            return {"message": "Request added successfully", "id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=404, detail="Failed to add Request")
    raise HTTPException(status_code=404, detail="Failed to add request - schedule or operator not found")


@router.delete("/requests/delete/{request_id}")
def delete_request(request_id: str):
    result = requests_db.delete_request(request_id)
    if result.deleted_count:
        return {"message": "Request deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Request not found")
