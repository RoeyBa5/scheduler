from bson import ObjectId

from repository import collection_schedules
from repository import collection_groups
from repository import collection_availabilities

from models.models import Schedule
import repository.groups as groups_db
import repository.availabilities as availabilities_db
import repository.requests as requests_db
import repository.shifts as shifts_db


# collection_schedules = db['schedules']


def create_schedule(schedule: Schedule):
    return collection_schedules.insert_one(schedule.dict())


def get_schedules():
    schedules = list(collection_schedules.find({}))
    return [convert_unserializable(schedule) for schedule in schedules]


def get_schedule(schedule_id: str):
    schedule = collection_schedules.find_one({"_id": ObjectId(schedule_id)})
    if schedule:
        schedule = convert_unserializable(schedule)
    return schedule


def delete_schedule(schedule_id: str):
    schedule = collection_schedules.find_one_and_delete({"_id": ObjectId(schedule_id)})
    if schedule:
        for group_id in schedule['groups_ids']:
            groups_db.delete_group(group_id)
        availabilities_db.delete_availabilities_after_deletion(schedule_id=schedule_id)
        requests_db.delete_requests_after_deletion(schedule_id=schedule_id)
    return schedule


# get full schedule object:
# if generated - get all groups and shifts
# if not - get all workers data
def get_schedule_object(schedule_id: str):
    schedule = collection_schedules.find_one({"_id": ObjectId(schedule_id)})
    if schedule['is_generated']:
        groups = list(collection_groups.aggregate([
            {"$match": {"schedule_id": schedule_id}},
            {"$lookup": {
                "from": "shifts",
                "localField": "shifts_ids",
                "foreignField": "_id",
                "as": "shifts"}}
        ]))

        schedule['groups'] = convert_groups_object_serializable(groups)
        return convert_unserializable(schedule)
    else:
        return availabilities_db.get_availabilities(schedule_id)


# converts unserializable fields of schedule to str
def convert_unserializable(schedule):
    schedule['_id'] = str(schedule['_id'])
    schedule['start_time'] = str(schedule['start_time'])
    schedule['end_time'] = str(schedule['end_time'])
    schedule['groups_ids'] = [str(group_id) for group_id in schedule['groups_ids']]
    return schedule

def convert_groups_object_serializable(groups):
    return [[shifts_db.convert_unserializable(shift) for shift in group['shifts']] for group in groups]

def generate_schedule(schedule_id: str):
    result = collection_schedules.update_one({"_id": ObjectId(schedule_id)}, {"$set": {"is_generated": True}})
    if result.modified_count:
        return result
    return collection_schedules.update_one({"_id": ObjectId(schedule_id)}, {"$set": {"is_generated": False}})
