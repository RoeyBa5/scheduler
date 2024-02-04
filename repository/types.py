from bson import ObjectId

from repository import db
from models.models import Type

collection_types = db['types']
collection_shifts = db['shifts']


def add_type(type):
    return collection_types.insert_one(type.dict())


def delete_type(type_id: str):
    # remove type from shifts where type_id is in type_ids
    type = collection_types.find_one_and_delete({"_id": ObjectId(type_id)})
    if type:
        collection_shifts.update_many({"type_id": type_id}, {"$pull": {"type_id": type_id}})
    return type


# handles both get all groups and get groups of schedule
def update_type(type_id: str, type: Type):
    return collection_types.update_one({"_id": ObjectId(type_id)}, {"$set": type.dict()})


def get_types():
    types = list(collection_types.find({}))
    for type in types:
        type['_id'] = str(type['_id'])
    return types


def get_type(type_id: str):
    return collection_types.find_one({"_id": ObjectId(type_id)})
