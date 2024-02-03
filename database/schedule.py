from bson import ObjectId

from database import collection_schedules

from models.models import Schedule
import database.groups as groups_db
import database.availabilities as availabilities_db
import database.requests as requests_db
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


# converts unserializable fields of schedule to str
def convert_unserializable(schedule):
    schedule['_id'] = str(schedule['_id'])
    schedule['start_time'] = str(schedule['start_time'])
    schedule['end_time'] = str(schedule['end_time'])
    schedule['groups_ids'] = [str(group_id) for group_id in schedule['groups_ids']]
    return schedule
