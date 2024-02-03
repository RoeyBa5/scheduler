from typing import List

from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse

import database.shifts as shifts_db
import database.groups as groups_db
from api import router
from models.models import Shift


@router.post("/shifts/create/")
def add_shift(shift: Shift):
    group_exists = groups_db.get_group(shift.group_id)
    if group_exists:
        result, inserted_group_id = shifts_db.add_shift(shift)
        if result.modified_count:
            return {"message": "Shift added successfully", "shift_id": str(inserted_group_id)}
        else:
            raise HTTPException(status_code=404, detail="Failed to add shift to group")
    else:
        raise HTTPException(status_code=404, detail=f"Failed to find group with id {shift.group_id}")


@router.delete("/shifts/delete/{shift_id}")
def delete_shift(shift_id: str):
    result = shifts_db.delete_shift(shift_id)
    if result:

        return {"message": "Shift deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="No shift found with given ID to delete")

@router.delete("/shifts/delete-all/")
def delete_all_shifts():
    result = shifts_db.delete_all_shifts()
    if result.deleted_count:
        return {'message': 'All shifts deleted successfully', 'deleted_count': result.deleted_count}
    else:
        return HTTPException(status_code=404, detail="No shifts found")


@router.post("/shifts/{shift_id}")
def update_shift(shift_id: str, shift: Shift):
    result = shifts_db.update_shift(shift_id, shift)
    if result.modified_count:
        return {"message": "Shift updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Shift not found")


@router.get("/shifts/", response_model=List[Shift])
def get_shifts(group_id: str = Query(None)):
    result = shifts_db.get_shifts(group_id)
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
