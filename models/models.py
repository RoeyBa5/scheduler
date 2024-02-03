from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class Training(BaseModel):
    _id: str
    name: str


class Operator(BaseModel):
    _id: str
    name: str
    trainings_ids: List["str"] = []


class Schedule(BaseModel):
    _id: str
    name: str
    start_time: datetime  # Time can store date value as YYYY-MM-DD
    end_time: datetime
    groups_ids: List["str"] = []
    is_generated: bool = False


# a group (moked) is uniquely described by the triplet: schedule_id, name, date
class Group(BaseModel):
    _id: str
    schedule_id: str = Field(..., alias="schedule_id_")
    name: str
    start_time: datetime
    end_time: datetime
    shifts_ids: List["str"] = []


class Type(BaseModel):
    _id: str
    name: str
    num_of_operators: int


class Shift(BaseModel):
    _id: str
    group_id: str = Field(..., alias="group_id_")
    start_time: datetime
    end_time: datetime
    assignment: dict  # key : training_id, value: operator_id


class Availability(BaseModel):
    _id: str
    schedule_id: str
    operator_id: str
    start_time: datetime
    end_time: datetime


class Request(BaseModel):
    _id: str
    schedule_id: str
    operator_id: str
    start_time: datetime
    end_time: datetime
    description: str
    score: int

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
