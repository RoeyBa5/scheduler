from typing import List

from fastapi import HTTPException
from fastapi.responses import JSONResponse

import database.schedule as schedule_db
from api import router
from models.models import Schedule


# CRUD operations
@router.post("/schedules/")
def create_schedule(schedule: Schedule):
    result = schedule_db.create_schedule(schedule)
    if result.inserted_id:
        return {"message": "Schedule created successfully", "id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create schedule")


@router.get("/schedules/", response_model=List[Schedule])
def get_schedules():
    result = schedule_db.get_schedules()
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No schedules found")


@router.get("/schedules/{schedule_id}", response_model=Schedule)
def get_schedule(schedule_id: str):
    result = schedule_db.get_schedule(schedule_id)
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No schedules found")


@router.delete("/schedules/delete/{schedule_id}")
def delete_schedule(schedule_id: str):
    result = schedule_db.delete_schedule(schedule_id)
    if result.deleted_count:
        return {"message": "Schedule deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="schedule not found")
