from datetime import datetime
from typing import List

from pydantic import BaseModel, validator
from pydantic.alias_generators import to_camel

from solver.temp_models import Request2, Qualification


class Training(BaseModel):
    _id: str
    name: str


class Operator(BaseModel):
    _id: str
    name: str
    trainings_ids: List[str] = []


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
    schedule_id: str
    name: str
    subtitle: str
    start_time: datetime
    end_time: datetime
    shifts_ids: List["str"] = []


class Type(BaseModel):
    _id: str
    name: str
    required_trainings: List["str"]


class Shift(BaseModel):
    _id: str
    group_id: str
    type_id: str
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


# Bargo models
class Worker2(BaseModel):
    id: str
    name: str
    availability: str
    roles: list[Qualification]
    requests: set[Request2]

    def __hash__(self):
        return hash(self.id)

    class Config:
        alias_generator = to_camel


class SlotType(BaseModel):
    id: str
    name: str
    assigned_number: int
    required_roles: list[str]

    class Config:
        alias_generator = to_camel


class Slot2(BaseModel):
    id: str
    name: str
    type: SlotType
    start: datetime
    end: datetime
    assigned_workers: dict[Qualification, Worker2 | None]

    class Config:
        alias_generator = to_camel

    @validator("assigned_workers", pre=True)
    def _validate_assigned_workers(cls, assigned_workers):
        for k, v in assigned_workers.items():
            if v == {}:
                assigned_workers[k] = None
        return assigned_workers


class SingleSlot(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    qualification: Qualification
    description: str = ""
    pre_scheduled: Worker2 | None = None

    def __hash__(self):
        return hash(self.id)


class Group2(BaseModel):
    id: str
    title: str
    sub_title: str | None = None
    slots: list[Slot2]

    class Config:
        alias_generator = to_camel


class Day2(BaseModel):
    id: str
    date: datetime
    groups: list[Group2]
    workers_data: list[Worker2]

    class Config:
        alias_generator = to_camel


class Schedule2(BaseModel):
    id: str
    name: str
    days: list[Day2]
    is_generated: bool

    class Config:
        alias_generator = to_camel
