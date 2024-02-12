from typing import List

from fastapi import HTTPException
from fastapi.responses import JSONResponse

import repository.types as types_db
from api import router
from models.models import Type


@router.post("/types/create/")
def add_type(type: Type):
    result = types_db.add_type(type)
    if result.inserted_id:
        return {"message": "Type added successfully", "type_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=404, detail="Failed to add type")


@router.delete("/types/delete/{type_id}")
def delete_type(type_id: str):
    result = types_db.delete_type(type_id)
    if result:
        return {"message": "Type deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="No type found with given ID to delete")


@router.post("/types/{type_id}")
def update_type(type_id: str, type: Type):
    result = types_db.update_type(type_id, type)
    if result.modified_count:
        return {"message": "Type updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Type not found")


@router.get("/types/", response_model=List[Type])
def get_types():
    result = types_db.get_types()
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        return {"message": "No types found"}


@router.get("/types/{type_id}", response_model=Type)
def get_type(type_id: str):
    result = types_db.get_type(type_id)
    if result:
        result['_id'] = str(result['_id'])
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No type found with given ID")
