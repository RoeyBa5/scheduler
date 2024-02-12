from models.models import Training
from repository import db, object_id, execute_db

collection_trainings = db['trainings']
collection_operators = db['operators']


def create_training(training: Training):
    return execute_db(collection_trainings.insert_one, training.dict())


def get_trainings():
    trainings = list(execute_db(collection_trainings.find, {}))
    # Convert ObjectId to string for serialization
    for training in trainings:
        training['_id'] = str(training['_id'])
    return trainings


def get_training(training_id: str):
    return execute_db(collection_trainings.find_one, {"_id": object_id(training_id)})


def update_training(training_id: str, training: Training):
    return execute_db(collection_trainings.update_one, {"_id": object_id(training_id)}, {"$set": training.dict()})


def delete_training(training_id: str):
    training = execute_db(collection_trainings.find_one_and_delete, {"_id": object_id(training_id)})
    if training:
        # Remove the training_id from all operators' trainings_ids list
        execute_db(collection_operators.update_many, {"trainings_ids": training_id}, {"$pull": {"trainings_ids": training_id}})
    return training
