from typing import List

from fastapi import HTTPException
from fastapi.responses import JSONResponse

import database.operators as operators_db
from api import router
from models.models import Operator


@router.get("/")
def read_root():
    return {"message": "Hello World"}


# CRUD operations
@router.post("/operators/")
def create_operator(operator: Operator):
    result = operators_db.create_operator(operator)
    if result.inserted_id:
        return {"message": "Operator created successfully", "id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create operator")


@router.post("/operators/create")
def create_operators(operators: List[Operator]):
    result = operators_db.create_many_operators(operators)
    if result:
        return {"message": "Operator created successfully", "ids": str(result)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create operator")


@router.get("/operators/", response_model=List[Operator])
def get_operators():
    result = operators_db.get_operators()
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No operators found")


@router.get("/operators/{operator_id}")
def get_operator(operator_id: str):
    result = operators_db.get_operator(operator_id)
    if result:
        result['_id'] = str(result['_id'])
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="Operator not found")


@router.post("/operators/{operator_id}")
def update_operator(operator_id: str, operator: Operator):
    result = operators_db.update_operator(operator_id, operator)
    if result.modified_count:
        return {"message": "Operator updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Operator not found")


@router.delete("/operators/delete/{operator_id}")
def delete_operator(operator_id: str):
    result = operators_db.delete_operator(operator_id)
    if result.deleted_count:
        return {"message": "Operator deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Operator not found")


@router.delete("/operators/delete")
def delete_all_operators():
    result = operators_db.delete_all_operators()
    if result:
        return {'message': 'All operators deleted successfully', 'deleted_count': result.deleted_count}
    else:
        return HTTPException(status_code=404, detail="No operators found")
