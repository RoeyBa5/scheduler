from bson import ObjectId

from app.database import db
from app.database.schedule import collection_schedules

collection_groups = db['groups']


def add_group(group):
    result = collection_groups.insert_one(group.dict())
    return collection_schedules.update_one({"_id": ObjectId(group.schedule_id)},
                                           {"$push": {"group_ids": ObjectId(result.inserted_id)}}), result.inserted_id


def remove_group(group_id: str):
    # remove group from schedule where schedule_id = result.schedule_id
    group = collection_groups.find_one_and_delete({"_id": ObjectId(group_id)})
    if group:
        return collection_schedules.update_one({"_id": ObjectId(group['schedule_id'])},
                                               {"$pull": {"group_ids": ObjectId(group_id)}})
    return None


# handles both get all groups and get groups of schedule
def get_groups(schedule_id: str):
    if schedule_id:
        groups = list(collection_groups.find({"schedule_id": schedule_id}))
    else:
        groups = list(collection_groups.find({}))
    return [convert_unserializable(group) for group in groups]


def get_group(group_id: str):
    group = collection_groups.find_one({"_id": ObjectId(group_id)})
    return convert_unserializable(group)


# converts unserializable fields of group to str
def convert_unserializable(group):
    if group:
        group['_id'] = str(group['_id'])
        group['start_time'] = str(group['start_time'])
        group['end_time'] = str(group['end_time'])
        group['shifts_ids'] = [str(shift_id) for shift_id in group['shifts_ids']]
    return group
