from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel

from solver.temp_models import Request2


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


class Qualification(Enum):
    TOL_OPERATOR = 'tol_operator'
    TOL_COMMANDEER = 'tol_commander'
    HOZI_OPEARTOR = 'hozi_operator'
    HOZI_COMMANDER = 'hozi_commander'
    HEAVY_OPERATOR = 'heavy_operator'
    HEAVY_COMMANDEER = 'heavy_commander'
    SIUA_SHLISHI = 'siua_shlishi'
    SIUA_OPERATOR = 'siua_operator'
    SIUA_COMMANDER = 'siua_commander'
    MOVIL = 'movil'
    KARKAI = 'karkai'


# Bargo models
class Worker2(BaseModel):
    id: str
    name: str
    availability: str
    roles: list[Qualification]
    requests: set[Request2]

    def __hash__(self):
        return hash(self.id)


class Slot2(BaseModel):
    id: str
    name: str
    type: str
    start: datetime
    end: datetime
    assigned_workers: dict[Qualification, Worker2]


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
    name: str
    slots: list[Slot2]


class Day2(BaseModel):
    id: str
    date: datetime
    groups: list[Group2]
    workersData: list[Worker2]


class Schedule2(BaseModel):
    id: str
    name: str
    days: list[Day2]
    isGenerated: bool
