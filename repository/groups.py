from bson import ObjectId

from repository import collection_groups
from repository import collection_schedules
from repository import collection_shifts


# collection_groups = db['groups']

def add_group(group):
    result = collection_groups.insert_one(group.dict())
    return collection_schedules.update_one({"_id": ObjectId(group.schedule_id)},
                                           {"$push": {"groups_ids": ObjectId(result.inserted_id)}}), result.inserted_id


def delete_group(group_id: str):
    group = collection_groups.find_one_and_delete({"_id": ObjectId(group_id)})
    if group:
        # collection_shifts.delete_many({"group_id": group_id})
        shifts_to_delete = group['shifts_ids']
        for shift_id in shifts_to_delete:
            collection_shifts.delete_one({"_id": shift_id})

        return collection_schedules.update_one({"_id": ObjectId(group['schedule_id'])},
                                               {"$pull": {"groups_ids": ObjectId(group_id)}})
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


def rename_group(group_id: str, new_name: str):
    return collection_groups.update_one({"_id": ObjectId(group_id)}, {"$set": {"name": new_name}})


# converts unserializable fields of group to str
def convert_unserializable(group):
    if group:
        group['_id'] = str(group['_id'])
        group['start_time'] = str(group['start_time'])
        group['end_time'] = str(group['end_time'])
        group['shifts_ids'] = [str(shift_id) for shift_id in group['shifts_ids']]
    return group
