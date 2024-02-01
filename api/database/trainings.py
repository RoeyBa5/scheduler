from typing import List

from bson import ObjectId

from app.database import db
from app.models.models import Training

collection_trainings = db['trainings']


def create_training(training: Training):
    return collection_trainings.insert_one(training.dict())

def get_trainings():
    trainings = list(collection_trainings.find({}))
    # Convert ObjectId to string for serialization
    for training in trainings:
        training['_id'] = str(training['_id'])
    return trainings


def get_training(training_id: str):
    return collection_trainings.find_one({"_id": ObjectId(training_id)})


def update_training(training_id: str, training: Training):
    return collection_trainings.update_one({"_id": ObjectId(training_id)}, {"$set": training.dict()})


def delete_training(training_id: str):
    return collection_trainings.delete_one({"_id": ObjectId(training_id)})


def delete_all_trainings():
    return collection_trainings.delete_many({})
