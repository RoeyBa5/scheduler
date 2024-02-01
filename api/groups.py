from typing import List

from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse

import database.groups as groups_db
import database.schedule as schedule_db
from api import router
from models.models import Group


@router.post("/groups/add/")
def add_group(group: Group):
    schedule_exists = schedule_db.get_schedule(group.schedule_id)
    if schedule_exists:
        result, inserted_group_id = groups_db.add_group(group)
        if result.modified_count:
            return {"message": "Group added successfully", "group_id": str(inserted_group_id)}
        else:
            raise HTTPException(status_code=404, detail="Failed to add group to schedule")
    else:
        raise HTTPException(status_code=404, detail=f"Failed to add find schedule with id {group.schedule_id}")


@router.delete("/groups/remove/{group_id}")
def remove_group(group_id: str):
    result = groups_db.remove_group(group_id)
    if result:
        return {"message": "Group deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Failed to remove group from schedule")


# handles both get all groups and get groups of schedule (if passed as query param)
@router.get("/groups/", response_model=List[Group])
def get_groups(schedule_id: str = Query(None)):
    result = groups_db.get_groups(schedule_id)
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No groups found")


@router.get("/groups/{group_id}")
def get_group(group_id: str):
    result = groups_db.get_group(group_id)
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No group found with given id")
