from bson import ObjectId

from repository import collection_requests
from models.models import Request


# Schedule and operator ids are optional
def get_requests(schedule_id: str = None, operator_id: str = None):
    query = {}
    query.update({"schedule_id": schedule_id} if schedule_id else {})
    query.update({"operator_id": operator_id} if operator_id else {})
    result = collection_requests.find(query)
    return [convert_unserializable(res) for res in list(result)]


def add_request(request: Request):
    return collection_requests.insert_one(request.dict())


def update_request(request_id: str, request: Request):
    return collection_requests.update_one({"_id": ObjectId(request_id)}, {"$set": request.dict()})


def delete_request(request_id: str):
    return collection_requests.delete_one({"_id": ObjectId(request_id)})


def delete_requests_after_deletion(schedule_id: str = None, operator_id: str = None):
    if schedule_id:
        return collection_requests.delete_many({"schedule_id": schedule_id})
    return collection_requests.delete_many({"operator_id": operator_id})


# converts unserializable fields of request to str
def convert_unserializable(request):
    if request:
        request['_id'] = str(request['_id'])
        request['start_time'] = str(request['start_time'])
        request['end_time'] = str(request['end_time'])
    return request


def delete_all():
    return collection_requests.delete_many({})