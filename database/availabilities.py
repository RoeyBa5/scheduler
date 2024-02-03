from bson import ObjectId

from database import collection_availabilities
from models.models import Availability

"""
db integrity:
- schedule delete - delete all schedule's availabilities
- operator delete - delete all operator's availabilities
- add availability - check for no duplications - NOT CHECKING
"""


# Schedule and operator ids are optional
def get_availabilities(schedule_id: str, operator_id: str):
    if schedule_id:
        if operator_id:
            # schedule and operator
            result = collection_availabilities.find(
                {"schedule_id": schedule_id, "operator_id": operator_id})
        else:
            # only schedule
            result = collection_availabilities.find({"schedule_id": schedule_id})
    elif operator_id:
        # only operator
        result = collection_availabilities.find({"operator_id": operator_id})
    else:
        # neither
        result = collection_availabilities.find({})
    return [convert_unserializable(res) for res in list(result)]


def add_availability(availability: Availability):
    return collection_availabilities.insert_one(availability.dict())


def delete_availability(availability_id: str):
    return collection_availabilities.delete_one({"_id": ObjectId(availability_id)})


def delete_availabilities_after_deletion(schedule_id: str = "", operator_id: str = ""):
    if schedule_id:
        return collection_availabilities.delete_many({"schedule_id": schedule_id})
    return collection_availabilities.delete_many({"operator_id": operator_id})


# converts unserializable fields of availability to str
def convert_unserializable(availability):
    if availability:
        availability['_id'] = str(availability['_id'])
        availability['start_time'] = str(availability['start_time'])
        availability['end_time'] = str(availability['end_time'])
    return availability
