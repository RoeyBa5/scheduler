from bson import ObjectId

from repository import db
from models.models import Shift
from repository import collection_groups
from repository import collection_shifts
# collection_shifts = db['shifts']


def add_shift(shift: Shift):
    result = collection_shifts.insert_one(shift.dict())
    # add the shift_id to the relevant groups shifts_ids
    return collection_groups.update_one({"_id": ObjectId(shift.group_id)},
                                        {"$push": {"shifts_ids": ObjectId(result.inserted_id)}}), result.inserted_id


def delete_shift(shift_id: str):
    shift = collection_shifts.find_one_and_delete({"_id": ObjectId(shift_id)})
    # before returning make sure to delete the shift from its group
    if shift:
        return collection_groups.update_one({"_id": ObjectId(shift['group_id'])},
                                            {"$pull": {"shifts_ids": ObjectId(shift_id)}})
    return None


def delete_all_shifts():
    result = collection_shifts.delete_many({})
    if result:
        collection_groups.update_many({}, {"$set": {"shifts_ids": []}})
    return result


# a different group_id will not be considered
def update_shift(shift_id: str, shift: Shift):
    allowed_fields = {"start_time", "end_time", "type_id", "assignment"}
    updated_fields = {key: value for key, value in shift.dict().items() if key in allowed_fields}
    if not updated_fields:
        return None  # No valid fields to update
    return collection_shifts.update_one({"_id": ObjectId(shift_id)}, {"$set": updated_fields})


def get_shifts(group_id: str):
    if group_id:
        shifts = list(collection_shifts.find({"group_id": group_id}))
    else:
        shifts = list(collection_shifts.find({}))
    return [convert_unserializable(shift) for shift in shifts]


def get_shift(shift_id: str):
    shift = collection_shifts.find_one({"_id": ObjectId(shift_id)})
    return convert_unserializable(shift)


# converts unserializable fields of shift to str
def convert_unserializable(shift):
    if shift:
        shift['_id'] = str(shift['_id'])
        shift['start_time'] = str(shift['start_time'])
        shift['end_time'] = str(shift['end_time'])
    return shift
