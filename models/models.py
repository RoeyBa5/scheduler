from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Qualification(BaseModel):
    id(str)
    name: str


class Operator(BaseModel):
    id(str)
    name: str
    trainings: List[Qualification]


class Schedule(BaseModel):
    id(str)
    start_time: datetime  # Time can store date value as YYYY-MM-DD
    end_time: datetime
    group_ids: List["str"] = []


# a group (moked) is uniquely described by the triplet: schedule_id, name, date
class Group(BaseModel):
    id(str)
    schedule_id: Optional[str] = Field(None, alias="schedule_id_")
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
    schedule_id: Optional[str] = Field(None, alias="schedule_id_")
    group_id: Optional[str] = Field(None, alias="group_id_")
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
"""
class Schedule(BaseModel):
    _id: str
    name: str
    start_time: datetime
    end_time: datetime
    is_generated: bool


class Group(BaseModel):
    _id: str
    schedule: Schedule
    name: str


class Slot(BaseModel):
    _id: str
    operator: Operator | None
    qualification: Qualification


class Shift(BaseModel):
    _id: str
    # foreign key to group
    group: Group
    start_time: datetime
    end_time: datetime
    slots: list[Slot]


class Operator(BaseModel):
    name: str
    qualifications: list[Qualification]


class Availability(BaseModel):
    _id: str
    schedule: Schedule
    operator: Operator
    start_time: datetime
    end_time: datetime


class Request(BaseModel):
    _id: str
    schedule: Schedule
    operator: Operator
    start_time: datetime
    end_time: datetime
    description: str
    score: int
"""
