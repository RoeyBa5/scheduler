# api/shifts.py

from typing import List

from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse

import app.database.shifts as shifts_db
from app.api import router
from app.models.models import Shift


@router.post("/shifts/create/")
def add_shift(shift: Shift):
    result = shifts_db.add_shift(shift)
    if result:
        return {"message": "Shift added successfully", "shift_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=404, detail="Failed to add shift. Couldn't find matching group")


@router.delete("/shifts/delete/{shift_id}")
def delete_shift(shift_id: str):
    result = shifts_db.delete_shift(shift_id)
    if result:

        return {"message": "Shift deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="No shift found with given ID to delete")


@router.post("/shifts/{shift_id}")
def update_shift(shift_id: str, shift: Shift):
    result = shifts_db.update_shift(shift_id, shift)
    if result.modified_count:
        return {"message": "Shift updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Shift not found")


@router.get("/shifts/", response_model=List[Shift])
def get_shifts():
    result = shifts_db.get_shifts()
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No shifts found")


@router.get("/shifts/{shift_id}", response_model=Shift)
def get_shift(shift_id: str):
    result = shifts_db.get_shift(shift_id)
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No shift found with given ID")
