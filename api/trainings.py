from typing import List

from fastapi import HTTPException
from fastapi.responses import JSONResponse

import repository.trainings as trainings_db
from api import router
from models.models import Training


# CRUD operations
@router.post("/trainings/create/")
def create_training(training: Training):
    result = trainings_db.create_training(training)
    if result.inserted_id:
        return {"message": "trainings created successfully", "id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create trainings")


@router.get("/trainings/", response_model=List[Training])
def get_trainings():
    result = trainings_db.get_trainings()
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        return {"message": "No trainings found"}


@router.get("/trainings/{training_id}")
def get_training(training_id: str):
    result = trainings_db.get_training(training_id)
    if result:
        result['_id'] = str(result['_id'])
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="Training not found")


@router.post("/trainings/{training_id}")
def update_training(training_id: str, training: Training):
    result = trainings_db.update_training(training_id, training)
    if result.modified_count:
        return {"message": "Training updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Training not found")


@router.delete("/trainings/delete/{training_id}")
def delete_training(training_id: str):
    training = trainings_db.delete_training(training_id)
    if training:
        return {"message": "Training deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Training not found")
