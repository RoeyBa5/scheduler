# from copy import deepcopy
#
# import pandas as pd
# from ortools.sat.python import cp_model
#
# from solver.data_loader import load_slots, load_operators
# from temp_models import Placement, Group, PlacementModel, PlacementModelConfig, Qualification
# from rules import is_night_slot, in_interval, min_hours_gap_between_slot
#
# KARKAI_MULTIPLIER = 0.6
#
# shifts_to_place = load_slots()
# operators = load_operators()
# operators_to_place = [operator for operator in operators if operator.auto_slot]
# shifts_by_day = {}
# for shift in shifts_to_place:
#     if shift.start_time.date() not in shifts_by_day:
#         shifts_by_day[shift.start_time.date()] = []
#     shifts_by_day[shift.start_time.date()].append(shift)
#
#
# def get_base_model(strict: bool) -> PlacementModel:
#     model = cp_model.CpModel()
#     # Create the variables
#     placements = {}
#     placements_by_operator = {}
#     for shift in shifts_to_place:
#         if shift.pre_scheduled:
#             pre_scheduled_operator = next(
#                 (operator for operator in operators if operator.name == shift.pre_scheduled), None)
#             if pre_scheduled_operator:
#                 placements[Placement(pre_scheduled_operator, shift)] = model.NewBoolVar(
#                     f"placement_operator:{pre_scheduled_operator.id}_shift:{shift.id}")
#                 if pre_scheduled_operator not in placements_by_operator:
#                     placements_by_operator[pre_scheduled_operator] = []
#                 placements_by_operator[pre_scheduled_operator].append(shift)
#                 continue
#         # constraints for operator, at the moment we work with availability only
#         for operator in operators_to_place:
#             #     overlaps = []
#             #     for cons in operator.constraints:
#             #         shift_interval = pd.Interval(left=pd.Timestamp(shift.start_time), right=pd.Timestamp(shift.end_time))
#             #         cons_internal = pd.Interval(left=pd.Timestamp(cons.start), right=pd.Timestamp(cons.end))
#             #         overlap = shift_interval.overlaps(cons_internal)
#             #         overlaps.append(overlap)
#             #     if len(overlaps) > 0 and any(overlaps):
#             #         continue
#
#             if shift.qualification in operator.qualifications and any(
#                     [availability.start <= shift.start_time <= availability.end
#                      and availability.start <= shift.end_time <= availability.end
#                      for availability in operator.availabilities]):
#                 placements[Placement(operator, shift)] = model.NewBoolVar(
#                     f"placement_operator:{operator.id}_shift:{shift.id}")
#                 if operator not in placements_by_operator:
#                     placements_by_operator[operator] = []
#                 placements_by_operator[operator].append(shift)
#
#     # Add constaints that each shift must be filled by exactly one operator
#     vars = []
#     for shift in shifts_to_place:
#         # if the shift is pre scheduled, make sure it is assigned to the operator
#         if shift.pre_scheduled:
#             pre_scheduled_operator = next(
#                 (operator for operator in operators if operator.name == shift.pre_scheduled), None)
#             model.Add(placements[Placement(pre_scheduled_operator, shift)] == 1)
#             continue
#
#         placements_per_shift = sum(placements[Placement(operator, shift)] for operator in operators_to_place
#                                    if Placement(operator, shift) in placements)
#         if strict:
#             model.Add(placements_per_shift == 1)
#         else:
#             vars.append(placements_per_shift)
#             model.Add(placements_per_shift <= 1)
#     if not strict:
#         model.AddMaxEquality(1, vars)
#
#     # Add constraint that each operator should have at least 4 hours of rest between shifts
#     for operator, shifts in placements_by_operator.items():
#         for shift in shifts:
#             for other_shift in shifts:
#                 if shift != other_shift and not min_hours_gap_between_slot(shift, other_shift):
#                     model.Add(
#                         placements[Placement(operator, shift)] + placements[Placement(operator, other_shift)] <= 1
#                     )
#
#     # Add constraint that each operator can do up to 12 hours of work per 24 hours
#     for operator, shifts in placements_by_operator.items():
#         for shift in shifts:
#             # This constraint not valid for KARKAI
#             if shift.qualification == Qualification.KARKAI:
#                 continue
#             close_shifts = [other_shift for other_shift in shifts
#                             if in_interval(shift, other_shift, 24)]
#             model.Add(
#                 sum(placements[Placement(operator, other_shift)] *
#                     int((other_shift.end_time - other_shift.start_time).total_seconds() // 3600) for other_shift
#                     in
#                     close_shifts
#                     if Placement(operator, other_shift) in placements) <= 12
#             )
#             close_shifts = [other_shift for other_shift in shifts_to_place
#                             if in_interval(shift, other_shift, 12)]
#             model.Add(
#                 sum(placements[Placement(operator, other_shift)] *
#                     int((other_shift.end_time - other_shift.start_time).total_seconds() // 3600) for other_shift in
#                     close_shifts
#                     if Placement(operator, other_shift) in placements) <= 8
#             )
#         return PlacementModel(model=model, placements=placements, placements_by_operator=placements_by_operator)
#
#
# def get_model_with_configurable_constraints(model: PlacementModel, config: PlacementModelConfig) -> PlacementModel:
#     # Add constarint that minimize the amount of nights for each operator.
#     night_count = len(
#         [shift for shift in shifts_to_place if is_night_slot(shift)]) / len(
#         operators_to_place)
#     for operator in operators_to_place:
#         night_count_per_op = sum(
#             model.placements[Placement(operator, shift)]
#             for shift in shifts_to_place if Placement(operator, shift) in model.placements
#             if is_night_slot(shift)
#         )
#         model.model.Add(night_count_per_op <= int(night_count * config.balance_ratio))
#         model.model.Add(night_count_per_op >= int(night_count * 1 / config.balance_ratio))
#
#     total_seconds_to_assign = sum(
#         int((shift.end_time - shift.start_time).total_seconds()) * (KARKAI_MULTIPLIER if shift.qualification ==
#                                                                                          Qualification.KARKAI else 1)
#         for shift in shifts_to_place)
#     avg_shifts_per_operator = total_seconds_to_assign / len(operators_to_place)
#     # make sure each operator has at least 80% of the average hours and at most 120% of the average hours
#     for operator in operators_to_place:
#         shifts_count = sum(
#             model.placements[Placement(operator, shift)] * int((shift.end_time - shift.start_time).total_seconds() * (
#                 KARKAI_MULTIPLIER if shift.qualification == Qualification.KARKAI else 1)) for shift in
#             shifts_to_place if
#             Placement(operator, shift) in model.placements
#         )
#         model.model.Add(shifts_count <= int(avg_shifts_per_operator * config.balance_ratio))
#         model.model.Add(int(avg_shifts_per_operator * 1 / config.balance_ratio) <= shifts_count)
#
#     # maximize the number of requests that are fulfilled
#     requests_fulfilled_vars = []
#     for operator in operators_to_place:
#         score = []
#         for request in operator.requests:
#             for shift in shifts_to_place:
#                 shift_interval = pd.Interval(left=pd.Timestamp(shift.start_time), right=pd.Timestamp(shift.end_time))
#                 request_interval = pd.Interval(left=pd.Timestamp(request.start), right=pd.Timestamp(request.end))
#                 overlap = shift_interval.overlaps(request_interval)
#                 score.append(-1 * model.placements[Placement(operator, shift)] * request.score
#                              if Placement(operator, shift) in model.placements
#                                 and overlap else 0)
#         requests_fulfilled_vars.append(sum(score))
#
#     model.model.Maximize(sum(requests_fulfilled_vars))
#
#     # for the marathon group, minimize the days that each operator does more than 1 shift
#
#     for operator in [operator for operator in operators if operator.group == Group.MARATHON]:
#         # minimize the days that each operator does more than 1 shift
#         vars = []
#         for day, shifts in shifts_by_day.items():
#             shifts_count = sum(
#                 model.placements[Placement(operator, shift)] for shift in shifts if
#                 Placement(operator, shift) in model.placements
#             )
#             vars.append(shifts_count)
#         model.model.AddMaxEquality(1, vars)
#
#     return model
#
#
# def print_solution(model: PlacementModel, solver: cp_model.CpSolver):
#     for operator in operators:
#         print(f"Operator {operator.name} is assigned to the following shifts:")
#         for shift in shifts_to_place:
#             if Placement(operator, shift) in model.placements and solver.Value(
#                     model.placements[Placement(operator, shift)]):
#                 print(f"Shift {shift.description} {shift.qualification} from {shift.start_time} to {shift.end_time}")
#
#     print("''''''''''''''")
#
#     print("Here some statics for the solution quality:")
#     # Number of night shifts per operator
#
#     for operator in operators_to_place:
#         print(
#             f"Operator {operator.name} has {sum(solver.Value(model.placements[Placement(operator, shift)]) for shift in shifts_to_place if Placement(operator, shift) in model.placements and is_night_slot(shift))} night shifts")
#
#     print("''''''''''''''")
#     # Number of hours per operator
#     for operator in operators_to_place:
#         print(
#             f"Operator {operator.name} has {sum(solver.Value(model.placements[Placement(operator, shift)]) * int((shift.end_time - shift.start_time).total_seconds() / 60 / 60) for shift in shifts_to_place if Placement(operator, shift) in model.placements)} hours")
#
#     print("''''''''''''''")
#     # Total score of fulfilled requests
#     for operator in operators_to_place:
#         # go over all requests and for each one check if there is a shift overlap, if so, subtract the score from 0
#         score = 0
#         for request in operator.requests:
#             for shift in shifts_to_place:
#                 shift_interval = pd.Interval(left=pd.Timestamp(shift.start_time), right=pd.Timestamp(shift.end_time))
#                 request_interval = pd.Interval(left=pd.Timestamp(request.start), right=pd.Timestamp(request.end))
#                 overlap = shift_interval.overlaps(request_interval)
#                 score += -1 * solver.Value(model.placements[Placement(operator, shift)]) * request.score if Placement(
#                     operator,
#                     shift) in model.placements and overlap else 0
#         print(f"Operator {operator.name} has a total score of {score}")
#
#     print("''''''''''''''")
#     # print the result of the std per marathon operator
#     for operator in [operator for operator in operators_to_place if operator.group == Group.MARATHON]:
#         # minimize the days that each operator does more than 1 shift
#         vars = []
#         for day, shifts in shifts_by_day.items():
#             shifts_count = sum(
#                 solver.Value(model.placements[Placement(operator, shift)]) for shift in shifts if
#                 Placement(operator, shift) in model.placements
#             )
#             vars.append(shifts_count)
#         avg = sum(vars) * (1 / len(vars))
#         print(f"Operator {operator.name} has a std of {sum((var - avg) ** 2 for var in vars) / len(vars)}")
#
#     # print per shift the operators that are assigned to it
#     for shift in shifts_to_place:
#         print(
#             f"Shift {shift.description} {shift.qualification} from {shift.start_time} to {shift.end_time} has the following operators assigned:")
#         for operator in operators:
#             if Placement(operator, shift) in model.placements and solver.Value(
#                     model.placements[Placement(operator, shift)]):
#                 print(f"Operator {operator.name}")
#
#     # Visualize the solution in a GANT chart
#     import plotly.figure_factory as ff
#
#     fig = ff.create_gantt(
#         [
#             dict(Task=f"Operator {operator.name}", Start=shift.start_time, Finish=shift.end_time)
#             for operator in operators for shift in shifts_to_place
#             if Placement(operator, shift) in model.placements and solver.Value(
#             model.placements[Placement(operator, shift)])
#         ],
#         show_colorbar=True,
#         group_tasks=True,
#         showgrid_x=True,
#         title="Shifts assignment"
#     )
#     fig.show()
#
#
# def run_model(base_model) -> bool:
#     config = PlacementModelConfig()
#     for i in range(20):
#         current_model = get_model_with_configurable_constraints(deepcopy(base_model), config)
#         solver = cp_model.CpSolver()
#         status = solver.Solve(current_model.model)
#         if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
#             print_solution(current_model, solver)
#             return True
#         config = PlacementModelConfig(
#             balance_ratio=config.balance_ratio * 1.01,
#         )
#     return False
#
#
# base_model = get_base_model(strict=True)
# res = run_model(base_model)
#
# if not res:
#     base_model = get_base_model(strict=False)
#     run_model(base_model)
