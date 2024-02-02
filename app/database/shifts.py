# database/shifts.py

from bson import ObjectId

from app.database import db
import app.database.groups as groups_db
from app.models.models import Shift

collection_shifts = db['shifts']


def add_shift(shift: Shift):
    # check that group exists
    group = groups_db.get_group(shift.group_id)
    if group:
        result = collection_shifts.insert_one(shift.dict())
        # add the shift_id to the relevant groups shifts_ids
        # use groups_db.update_group
        group['shifts_ids'].append(result.inserted_id)
        updated = groups_db.collection_groups.update_one({"_id": ObjectId(group['_id'])}, {"$set": group})
        if updated:
            return result
    return None


def delete_shift(shift_id: str):
    shift = collection_shifts.find_one_and_delete({"_id": ObjectId(shift_id)})
    # before returning make sure to delete the shift from its group

    return shift


def update_shift(shift_id: str, shift: Shift):
    allowed_fields = {"start_time", "end_time", "type_id", "assigned_operators_ids"}
    updated_fields = {key: value for key, value in shift.dict().items() if key in allowed_fields}
    if not updated_fields:
        return None  # No valid fields to update
    return collection_shifts.update_one({"_id": ObjectId(shift_id)}, {"$set": updated_fields})


def get_shifts():
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
        shift['assigned_operators_ids'] = [str(operator_id) for operator_id in shift['assigned_operators_ids']]
    return shift
