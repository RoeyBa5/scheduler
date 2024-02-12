from repository import object_id, execute_db

from repository import collection_availabilities
from models.models import Availability

"""
db integrity:
- schedule delete - delete all schedule's availabilities
- operator delete - delete all operator's availabilities
- add availability - check for no duplications - NOT CHECKING
"""


# Schedule and operator ids are optional
def get_availabilities(schedule_id: str = None, operator_id: str = None):
    query = {}
    query.update({"schedule_id": schedule_id} if schedule_id else {})
    query.update({"operator_id": operator_id} if operator_id else {})
    result = execute_db(collection_availabilities.find, query)
    return [convert_unserializable(res) for res in list(result)]


def add_availability(availability: Availability):
    return execute_db(collection_availabilities.insert_one, availability.dict())


def delete_availability(availability_id: str):
    return execute_db(collection_availabilities.delete_one, {"_id": object_id(availability_id)})


def delete_availabilities_after_deletion(schedule_id: str = None, operator_id: str = None):
    if schedule_id:
        return execute_db(collection_availabilities.delete_many, {"schedule_id": schedule_id})
    return execute_db(collection_availabilities.delete_many, {"operator_id": operator_id})


# converts unserializable fields of availability to str
def convert_unserializable(availability):
    if availability:
        availability['_id'] = str(availability['_id'])
        availability['start_time'] = str(availability['start_time'])
        availability['end_time'] = str(availability['end_time'])
    return availability


def delete_all():
    return execute_db(collection_availabilities.delete_many, {})
