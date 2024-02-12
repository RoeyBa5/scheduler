from typing import List

from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse

import repository.availabilities as availabilities_db
import repository.schedule as schedules_db
import repository.operators as operators_db
from api import router
from models.models import Availability


@router.get("/availabilities/", response_model=List[Availability])
def get_availabilities(schedule_id: str = Query(None), operator_id: str = Query(None)):
    schedule_exists = schedules_db.get_schedule(schedule_id)
    operator_exists = operators_db.get_operator(operator_id)
    if schedule_id and not schedule_exists:
        raise HTTPException(status_code=404, detail="Schedule provided but not found")
    if operator_id and not operator_exists:
        raise HTTPException(status_code=404, detail="Operator provided but not found")
    result = availabilities_db.get_availabilities(schedule_id, operator_id)
    return JSONResponse(content=result, media_type="application/json")


@router.post("/availabilities/create/")
def add_availability(availability: Availability):
    schedule_exists = schedules_db.get_schedule(availability.schedule_id)
    operator_exists = operators_db.get_operator(availability.operator_id)
    if schedule_exists and operator_exists:
        result = availabilities_db.add_availability(availability)
        if result.inserted_id:
            return {"message": "Availability added successfully", "id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=404, detail="Failed to add availability")
    raise HTTPException(status_code=404, detail="Failed to add availability - schedule or operator not found")


@router.delete("/availabilities/delete/{availability_id}")
def delete_availability(availability_id: str):
    result = availabilities_db.delete_availability(availability_id)
    if result.deleted_count:
        return {"message": "Availability deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Availability not found")


