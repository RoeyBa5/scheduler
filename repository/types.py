from models.models import Type
from repository import db, execute_db, object_id

collection_types = db['types']
collection_shifts = db['shifts']


def add_type(type: Type):
    return execute_db(collection_types.insert_one, type.dict())


def delete_type(type_id: str):
    # remove type from shifts where type_id is in type_ids
    type = execute_db(collection_types.find_one_and_delete, {"_id": object_id(type_id)})
    if type:
        execute_db(collection_shifts.update_many, {"type_id": type_id}, {"$set": {"type_id": ""}})
    return type


# handles both get all groups and get groups of schedule
def update_type(type_id: str, type: Type):
    return execute_db(collection_types.update_one, {"_id": object_id(type_id)}, {"$set": type.dict()})


def get_types():
    types = list(execute_db(collection_types.find, {}))
    for type in types:
        type['_id'] = str(type['_id'])
    return types


def get_type(type_id: str):
    return execute_db(collection_types.find_one, {"_id": object_id(type_id)})
