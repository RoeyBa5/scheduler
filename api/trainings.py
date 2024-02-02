from typing import List

from fastapi import HTTPException
from fastapi.responses import JSONResponse

import database.trainings as trainings_db
from api import router
from models.models import Qualification


# CRUD operations
@router.post("/trainings/")
def create_training(training: Qualification):
    result = trainings_db.create_training(training)
    if result.inserted_id:
        return {"message": "trainings created successfully", "id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create trainings")


@router.get("/trainings/", response_model=List[Qualification])
def get_trainings():
    result = trainings_db.get_trainings()
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No training found")


@router.get("/trainings/{training_id}")
def get_operator(training_id: str):
    result = trainings_db.get_training(training_id)
    if result:
        result['_id'] = str(result['_id'])
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="Training not found")


@router.post("/trainings/{training_id}")
def update_training(training_id: str, training: Qualification):
    result = trainings_db.update_operator(training_id, training)
    if result.modified_count:
        return {"message": "Training updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Training not found")


@router.delete("/trainings/delete/{training_id}")
def delete_training(training_id: str):
    result = trainings_db.delete_training(training_id)
    if result.deleted_count:
        return {"message": "Training deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Training not found")


@router.delete("/trainings/delete")
def delete_all_trainings():
    result = trainings_db.delete_all_trainings()
    if result:
        return {'message': 'All operators deleted successfully', 'deleted_count': result.deleted_count}
    else:
        return HTTPException(status_code=404, detail="No trainings found")
