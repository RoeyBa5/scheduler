from bson import ObjectId

from app.database import db
from app.models.models import Schedule, Group

collection_schedules = db['schedules']
collection_groups = db['groups']


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
    return collection_groups.delete_many({"schedule_id": schedule_id})


# converts unserializable fields of schedule to str
def convert_unserializable(schedule):
    schedule['_id'] = str(schedule['_id'])
    schedule['start_time'] = str(schedule['start_time'])
    schedule['end_time'] = str(schedule['end_time'])
    schedule['group_ids'] = [str(group_id) for group_id in schedule['group_ids']]
    return schedule
