from typing import List

from repository import object_id, execute_db

from repository import collection_operators
import repository.availabilities as availabilities_db
import repository.requests as requests_db
from models.models import Operator


def create_operator(operator: Operator):
    return execute_db(collection_operators.insert_one, operator.dict())


def create_many_operators(operators: List[Operator]):
    operators_dicts = [operator.dict() for operator in operators]
    result = execute_db(collection_operators.insert_many, operators_dicts)
    return result.inserted_ids


def get_operators():
    operators = list(execute_db(collection_operators.find, {}))
    for operator in operators:
        operator['_id'] = str(operator['_id'])
    return operators


def get_operator(operator_id: str):
    return execute_db(collection_operators.find_one, {"_id": object_id(operator_id)})


def update_operator(operator_id: str, operator: Operator):
    return execute_db(collection_operators.update_one, {"_id": object_id(operator_id)}, {"$set": operator.dict()})


def delete_operator(operator_id: str):
    result = execute_db(collection_operators.delete_one, {"_id": object_id(operator_id)})
    availabilities_db.delete_availabilities_after_deletion(operator_id=operator_id)
    requests_db.delete_requests_after_deletion(operator_id=operator_id)
    return result


def delete_all_operators():
    result = execute_db(collection_operators.delete_many, {})
    if result.deleted_count:
        availabilities_db.delete_all()
        requests_db.delete_all()
    return result


def add_training_to_operator(operator_id: str, training_id: str):
    # Add the training_id to the operator's trainings_ids list
    return execute_db(collection_operators.update_one, {"_id": object_id(operator_id)},
                      {"$push": {"trainings_ids": training_id}})


def remove_training_from_operator(operator_id: str, training_id: str):
    return execute_db(collection_operators.update_one, {"_id": object_id(operator_id)},
                      {"$pull": {"trainings_ids": training_id}})
