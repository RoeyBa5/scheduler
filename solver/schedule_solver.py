from copy import deepcopy

import pandas as pd
from ortools.sat.python import cp_model

from solver.rules import is_night_slot, in_interval, min_hours_gap_between_slot
from solver.temp_models import Placement, Group, PlacementModel, PlacementModelConfig, Qualification, Sector
from solver.temp_models import SingleSlot, Operator

KARKAI_MULTIPLIER = 0.6
SHIFTS_PER_MIL = 2


class NoSolutionFound(Exception):
    pass


"""
This class is responsible for solving the schedule problem.
It receives a list of slots and a list of operators and returns a list of placements.
"""


class ScheduleSolver:
    def __init__(self, slots: list[SingleSlot], operators: list[Operator]):
        self.slots = slots
        self.operators = operators

        self.placements = None

    def solve(self) -> list[Placement]:
        operators_to_place = [operator for operator in self.operators if operator.auto_slot]
        slots_by_day = {}
        for slot in self.slots:
            if slot.start_time.date() not in slots_by_day:
                slots_by_day[slot.start_time.date()] = []
            slots_by_day[slot.start_time.date()].append(slot)

        def get_base_model(strict: bool) -> PlacementModel:
            model = cp_model.CpModel()
            # Create the variables
            placements = {}
            placements_by_operator = {}
            for slot in self.slots:
                if slot.pre_scheduled:
                    pre_scheduled_operator = next(
                        (operator for operator in self.operators if operator.id == slot.pre_scheduled.id), None)
                    if pre_scheduled_operator:
                        placements[Placement(pre_scheduled_operator, slot)] = model.NewBoolVar(
                            f"placement_operator:{pre_scheduled_operator.id}_slot:{slot.id}")
                        if pre_scheduled_operator not in placements_by_operator:
                            placements_by_operator[pre_scheduled_operator] = []
                        placements_by_operator[pre_scheduled_operator].append(slot)
                        continue
                # constraints for operator, at the moment we work with availability only
                for operator in operators_to_place:
                    #     overlaps = []
                    #     for cons in operator.constraints:
                    #         slot_interval = pd.Interval(left=pd.Timestamp(slot.start_time), right=pd.Timestamp(slot.end_time))
                    #         cons_internal = pd.Interval(left=pd.Timestamp(cons.start), right=pd.Timestamp(cons.end))
                    #         overlap = slot_interval.overlaps(cons_internal)
                    #         overlaps.append(overlap)
                    #     if len(overlaps) > 0 and any(overlaps):
                    #         continue

                    if slot.qualification in operator.qualifications and any(
                            [availability.start <= slot.start_time <= availability.end
                             and availability.start <= slot.end_time <= availability.end
                             for availability in operator.availabilities]):
                        placements[Placement(operator, slot)] = model.NewBoolVar(
                            f"placement_operator:{operator.id}_slot:{slot.id}")
                        if operator not in placements_by_operator:
                            placements_by_operator[operator] = []
                        placements_by_operator[operator].append(slot)

            # Add constaints that each slot must be filled by exactly one operator
            vars = []
            for slot in self.slots:
                # if the slot is pre scheduled, make sure it is assigned to the operator
                if slot.pre_scheduled:
                    pre_scheduled_operator = next(
                        (operator for operator in self.operators if operator.id == slot.pre_scheduled.id), None)
                    if pre_scheduled_operator:
                        model.Add(placements[Placement(pre_scheduled_operator, slot)] == 1)
                        continue

                placements_per_slot = sum(placements[Placement(operator, slot)] for operator in operators_to_place
                                          if Placement(operator, slot) in placements)
                if strict:
                    model.Add(placements_per_slot == 1)
                else:
                    vars.append(placements_per_slot)
                    model.Add(placements_per_slot <= 1)
            if not strict:
                model.AddMaxEquality(1, vars)

            # Add constraint that each operator should have at least 4 hours of rest between slots
            for operator, slots in placements_by_operator.items():
                for slot in slots:
                    for other_slot in slots:
                        if slot != other_slot and not min_hours_gap_between_slot(slot, other_slot):
                            model.Add(
                                placements[Placement(operator, slot)] + placements[
                                    Placement(operator, other_slot)] <= 1
                            )

            # Add constraint that each operator can do up to 12 hours of work per 24 hours
            for operator, slots in placements_by_operator.items():
                for slot in slots:
                    # This constraint not valid for KARKAI
                    if slot.qualification == Qualification.KARKAI:
                        continue
                    close_slots = [other_slot for other_slot in slots
                                   if in_interval(slot, other_slot, 24)]
                    model.Add(
                        sum(placements[Placement(operator, other_slot)] *
                            int((other_slot.end_time - other_slot.start_time).total_seconds() // 3600) for other_slot
                            in
                            close_slots
                            if Placement(operator, other_slot) in placements) <= 12
                    )
                    close_slots = [other_slot for other_slot in self.slots
                                   if in_interval(slot, other_slot, 12)]
                    model.Add(
                        sum(placements[Placement(operator, other_slot)] *
                            int((other_slot.end_time - other_slot.start_time).total_seconds() // 3600) for other_slot
                            in
                            close_slots
                            if Placement(operator, other_slot) in placements) <= 8
                    )
            return PlacementModel(model=model, placements=placements, placements_by_operator=placements_by_operator)

        def get_model_with_configurable_constraints(model: PlacementModel,
                                                    config: PlacementModelConfig) -> PlacementModel:
            mil_ops = [op for op in operators_to_place if op.sector == Sector.MIL]
            not_mil_ops = [op for op in operators_to_place if op.sector != Sector.MIL]
            # Add constarint that minimize the amount of nights for each operator who is Mil
            for operator in mil_ops:
                night_count_per_op = sum(
                    model.placements[Placement(operator, slot)]
                    for slot in self.slots if Placement(operator, slot) in model.placements
                    if is_night_slot(slot)
                )
                model.model.Add(night_count_per_op <= int(SHIFTS_PER_MIL * config.balance_ratio / 2))
            # Add constarint that minimize the amount of nights for each operator who is not Mil.
            night_count = len(
                [slot for slot in self.slots if is_night_slot(slot) - SHIFTS_PER_MIL * len(mil_ops) / 2]) / len(
                operators_to_place)
            for operator in operators_to_place:
                night_count_per_op = sum(
                    model.placements[Placement(operator, slot)]
                    for slot in self.slots if Placement(operator, slot) in model.placements
                    if is_night_slot(slot)
                )
                model.model.Add(night_count_per_op <= int(night_count * config.balance_ratio))
                # model.model.Add(night_count_per_op >= int(night_count * 1 / config.balance_ratio))

            total_seconds_to_assign = sum(
                int((slot.end_time - slot.start_time).total_seconds()) * (KARKAI_MULTIPLIER if slot.qualification ==
                                                                                               Qualification.KARKAI else 1)
                for slot in self.slots)

            # # make sure each Mil does the amount of shifts per day
            for operator in mil_ops:
                slots_count = sum(
                    model.placements[Placement(operator, slot)] for slot in self.slots if
                    Placement(operator, slot) in model.placements
                )
                model.model.Add(slots_count <= int(SHIFTS_PER_MIL * config.balance_ratio))
                model.model.Add(slots_count >= int(SHIFTS_PER_MIL * 1 / config.balance_ratio))
            # make sure each operator who is not Mil has at least 80% of the average hours and at most 120% of the average hours
            if len(not_mil_ops) > 0:
                avg_slots_per_operator = (total_seconds_to_assign - SHIFTS_PER_MIL * 4 * 60 * 60 * len(mil_ops)) / len(
                    not_mil_ops)
                for operator in not_mil_ops:
                    slots_count = sum(
                        model.placements[Placement(operator, slot)] * int(
                            (slot.end_time - slot.start_time).total_seconds() * (
                                KARKAI_MULTIPLIER if slot.qualification == Qualification.KARKAI else 1)) for slot in
                        self.slots if
                        Placement(operator, slot) in model.placements
                    )
                    model.model.Add(slots_count <= int(avg_slots_per_operator * config.balance_ratio))
                    model.model.Add(int(avg_slots_per_operator * 1 / config.balance_ratio) <= slots_count)

            # maximize the number of requests that are fulfilled
            requests_fulfilled_vars = []
            for operator in operators_to_place:
                score = []
                for request in operator.requests:
                    for slot in self.slots:
                        slot_interval = pd.Interval(left=pd.Timestamp(slot.start_time),
                                                    right=pd.Timestamp(slot.end_time))
                        request_interval = pd.Interval(left=pd.Timestamp(request.start),
                                                       right=pd.Timestamp(request.end))
                        overlap = slot_interval.overlaps(request_interval)
                        score.append(-1 * model.placements[Placement(operator, slot)] * request.score
                                     if Placement(operator, slot) in model.placements
                                        and overlap else 0)
                requests_fulfilled_vars.append(sum(score))

            model.model.Maximize(sum(requests_fulfilled_vars))

            # for the marathon group, minimize the days that each operator does more than 1 slot
            for operator in [operator for operator in self.operators if operator.group == Group.MARATHON]:
                # minimize the days that each operator does more than 1 slot
                vars = []
                for day, slots in slots_by_day.items():
                    slots_count = sum(
                        model.placements[Placement(operator, slot)] for slot in slots if
                        Placement(operator, slot) in model.placements
                    )
                    vars.append(slots_count)
                model.model.AddMaxEquality(1, vars)

            return model

        def run_model(base_model) -> (PlacementModel, cp_model.CpSolver):
            config = PlacementModelConfig()
            for i in range(20):
                current_model = get_model_with_configurable_constraints(deepcopy(base_model), config)
                solver = cp_model.CpSolver()
                status = solver.Solve(current_model.model)
                if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
                    return current_model, solver
                config = PlacementModelConfig(
                    balance_ratio=config.balance_ratio * 1.01,
                )
            return None, None

        base_model = get_base_model(strict=True)
        model, solver = run_model(base_model)

        if not model or not solver:
            base_model = get_base_model(strict=False)
            model, solver = run_model(base_model)

        if not model or not solver:
            raise NoSolutionFound("No solution found for this schedule")

        self.placements = [placement for placement, var in model.placements.items() if solver.Value(var) == 1]
        return self.placements

# operators = load_operators()
# slots = load_slots()
# solution = ScheduleSolver(slots, operators).solve()
# for operator in operators:
#     op_slots = [placement.slot for placement in solution if placement.operator == operator]
#     print(f"Operator {operator.name}, from sector {operator.sector} has {len(op_slots)} slots")
#     night_slots = [slot for slot in op_slots if is_night_slot(slot)]
#     print(f"Operator {operator.name} has {len(night_slots)} night slots")
#     [print(f"Slot {slot.start_time} - {slot.end_time}") for slot in op_slots]
#     print('--------------------')
# pass
