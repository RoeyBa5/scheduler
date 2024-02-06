from typing import List

from fastapi import HTTPException, Query
from fastapi.responses import JSONResponse

import repository.groups as groups_db
import repository.schedule as schedule_db
from api import router
from models.models import Group


@router.post("/groups/create/")
def add_group(group: Group):
    schedule_exists = schedule_db.get_schedule(group.schedule_id)
    if schedule_exists:
        result, inserted_group_id = groups_db.add_group(group)
        if result.modified_count:
            return {"message": "Group added successfully", "group_id": str(inserted_group_id)}
        else:
            raise HTTPException(status_code=404, detail="Failed to add group to schedule")
    else:
        raise HTTPException(status_code=404, detail=f"Failed to find schedule with id {group.schedule_id}")


@router.delete("/groups/delete/{group_id}")
def remove_group(group_id: str):
    result = groups_db.delete_group(group_id)
    if result:
        return {"message": "Group deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="No group found with given ID to delete")


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


# group id as path param, new_name as query param
@router.post("/groups/rename/{group_id}")
def update_group(group_id: str, new_name: str):
    result = groups_db.rename_group(group_id, new_name)
    if result:
        return {"message": "Group renamed successfully"}
    else:
        raise HTTPException(status_code=404, detail="No group found with given id")
