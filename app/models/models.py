from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Optional


class Training(BaseModel):
    id(str)
    name: str


class Operator(BaseModel):
    id(str)
    name: str
    trainings_ids: List["str"] = []


class Schedule(BaseModel):
    id(str)
    start_time: datetime  # Time can store date value as YYYY-MM-DD
    end_time: datetime
    group_ids: List["str"] = []


# a group (moked) is uniquely described by the triplet: schedule_id, name, date
class Group(BaseModel):
    id(str)
    schedule_id: str = Field(..., alias="schedule_id_")
    name: str
    start_time: datetime
    end_time: datetime
    shifts_ids: List["str"] = []


class Type(BaseModel):
    id(str)
    name: str
    num_of_operators: int


class Shift(BaseModel):
    id(str)
    group_id: str = Field(..., alias="group_id_")
    start_time: datetime
    end_time: datetime
    type_id: str
    assigned_operators_ids: List["str"] = []




# # a slot is uniquely described by a set: schedule_id, group_id, shift, training
# class Slot(BaseModel):
#     id(str)
#     schedule_id: Optional[str] = Field(None, alias="schedule_id_")
#     group_id: Optional[str] = Field(None, alias="group_id_")
#     shift_id: Optional[str] = Field(None, alias="shift_id_")
#     training: Training
#     start_time: datetime
#     end_time: datetime
#     assigned_operator: Operator = None
