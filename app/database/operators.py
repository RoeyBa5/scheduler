from typing import List

from bson import ObjectId

from app.database import db
from app.models.models import Operator

collection_operators = db['operators']


def create_operator(operator: Operator):
    return collection_operators.insert_one(operator.dict())


def create_many_operators(operators: List[Operator]):
    operators_dicts = [operator.dict() for operator in operators]
    result = collection_operators.insert_many(operators_dicts)
    return result.inserted_ids


def get_operators():
    operators = list(collection_operators.find({}))
    # Convert ObjectId to string for serialization
    for operator in operators:
        operator['_id'] = str(operator['_id'])
    return operators


def get_operator(operator_id: str):
    return collection_operators.find_one({"_id": ObjectId(operator_id)})


def update_operator(operator_id: str, operator: Operator):
    return collection_operators.update_one({"_id": ObjectId(operator_id)}, {"$set": operator.dict()})


def delete_operator(operator_id: str):
    return collection_operators.delete_one({"_id": ObjectId(operator_id)})


def delete_all_operators():
    return collection_operators.delete_many({})


def add_training_to_operator(operator_id: str, training_id: str):
    # Add the training_id to the operator's trainings_ids list
    return collection_operators.update_one({"_id": ObjectId(operator_id)},
                                           {"$push": {"trainings_ids": training_id}})


def remove_training_from_operator(operator_id: str, training_id: str):
    return collection_operators.update_one({"_id": ObjectId(operator_id)},
                                           {"$pull": {"trainings_ids": training_id}})
