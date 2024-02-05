import dataclasses
import uuid
from datetime import datetime
from enum import Enum

from ortools.sat.python.cp_model import CpModel


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


class Sector(Enum):
    SADIR = 'sadir'
    HANHALA = 'hanhala'
    HATZAH = 'hatzah'
    LATZAT = 'latzat'
    MIL = 'mil'


@dataclasses.dataclass
class Request:
    start: datetime
    end: datetime
    description: str
    score: int


@dataclasses.dataclass
class OtherSlot:
    start: datetime
    end: datetime


class Group(Enum):
    SPRINT = "sprint"
    MARATHON = "marathon"


@dataclasses.dataclass
class Constraint:
    description: str
    start: datetime
    end: datetime


@dataclasses.dataclass
class Availability:
    start: datetime
    end: datetime


@dataclasses.dataclass
class Operator:
    id: int
    name: str
    sector: Sector
    qualifications: list[Qualification] = dataclasses.field(default_factory=list)
    group: Group = Group.SPRINT
    requests: list[Request] = dataclasses.field(default_factory=list)
    constraints: list[Constraint] = dataclasses.field(default_factory=list)
    availabilities: list[Availability] = dataclasses.field(default_factory=list)
    # other_shifts: list[OtherShift] = dataclasses.field(default_factory=list)
    auto_slot: bool = True

    def __hash__(self):
        return hash(self.id)


@dataclasses.dataclass
class Slot:
    id: uuid.UUID
    start_time: datetime
    end_time: datetime
    qualification: Qualification
    description: str = ""
    pre_scheduled: str = ""

    def __hash__(self):
        return hash(self.id)


@dataclasses.dataclass
class Placement:
    operator: Operator
    slot: Slot

    def __hash__(self):
        return hash((self.operator, self.slot))


@dataclasses.dataclass
class PlacementModel:
    model: CpModel
    placements: dict
    placements_by_operator: dict


@dataclasses.dataclass
class PlacementModelConfig:
    balance_ratio: float = 1.2
