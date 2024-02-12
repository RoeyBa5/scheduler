from typing import List

from fastapi import HTTPException
from fastapi.responses import JSONResponse

import repository.operators as operators_db
import repository.trainings as trainings_db
from api import router
from models.models import Operator


# CRUD operations
@router.post("/operators/create/")
def create_operator(operator: Operator):
    result = operators_db.create_operator(operator)
    if result.inserted_id:
        return {"message": "Operator created successfully", "id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=404, detail="Failed to create operator")


@router.post("/operators/create-many/")
def create_operators(operators: List[Operator]):
    result = operators_db.create_many_operators(operators)
    if result:
        return {"message": "Operators created successfully", "ids": str(result)}
    else:
        raise HTTPException(status_code=404, detail="Failed to create operator")


@router.get("/operators/", response_model=List[Operator])
def get_operators():
    result = operators_db.get_operators()
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        return {"message": "No operators found"}


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


@router.delete("/operators/delete-all/")
def delete_all_operators():
    result = operators_db.delete_all_operators()
    if result.deleted_count:
        return {'message': 'All operators deleted successfully', 'deleted_count': result.deleted_count}
    else:
        return HTTPException(status_code=404, detail="No operators found")


# add <training_id> to <operator_id> list of trainings - get params from query
@router.post("/operators/add-training/")
def add_training_to_operator(operator_id: str, training_id: str):
    operator = operators_db.get_operator(operator_id)
    training = trainings_db.get_training(training_id)
    if training and operator:
        if training_id not in operator.get("trainings_ids", []):
            result = operators_db.add_training_to_operator(operator_id, training_id)
            if result.modified_count:
                return {'message': 'training added successfully', 'modified count': result.modified_count}
            else:
                raise HTTPException(status_code=404, detail="Error: training not added")
        else:
            raise HTTPException(status_code=404, detail="Training already in operator's trainings list")
    raise HTTPException(status_code=404, detail="Operator or training ID not valid")


# remove <training_id> from <operator_id> list of trainings - get params from query
@router.post("/operators/remove-training/")
def remove_training_from_operator(operator_id: str, training_id: str):
    operator = operators_db.get_operator(operator_id)
    training = trainings_db.get_training(training_id)
    if training and operator:
        if training_id in operator.get("trainings_ids", []):
            result = operators_db.remove_training_from_operator(operator_id, training_id)
            if result.modified_count:
                return {'message': 'training removed successfully', 'modified count': result.modified_count}
            else:
                raise HTTPException(status_code=404, detail="Error: training not removed")
        else:
            raise HTTPException(status_code=404, detail="Training not found operator's trainings list")
    raise HTTPException(status_code=404, detail="Operator or training ID not valid")
