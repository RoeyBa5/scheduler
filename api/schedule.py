import logging
from copy import deepcopy
from datetime import timedelta
from typing import List

from fastapi import BackgroundTasks
from fastapi import HTTPException
from fastapi.responses import JSONResponse

import repository.schedule as schedule_db
from api import router
from models.models import Schedule, Schedule2, Worker2
from repository import collection_schedules2
from solver.schedule_solver import ScheduleSolver, NoSolutionFound
from solver.temp_models import SingleSlot, Operator, Availability, Sector, Placement


# CRUD operations
@router.post("/schedules/create")
def create_schedule(schedule: Schedule):
    result = schedule_db.create_schedule(schedule)
    if result.inserted_id:
        return {"message": "Schedule created successfully", "id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create schedule")


@router.get("/schedules/", response_model=List[Schedule])
def get_schedules():
    result = schedule_db.get_schedules()
    return JSONResponse(content=result, media_type="application/json")


# @router.get("/schedules/{schedule_id}", response_model=Schedule)
# def get_schedule(schedule_id: str):
#     result = schedule_db.get_schedule(schedule_id)
#     if result:
#         return JSONResponse(content=result, media_type="application/json")
#     else:
#         raise HTTPException(status_code=404, detail="No schedules found")


@router.get("/schedules/object/{schedule_id}", response_model=Schedule)
def get_schedule_object(schedule_id: str):
    schedule = schedule_db.get_schedule(schedule_id)
    if schedule:
        result = schedule_db.get_schedule_object(schedule)
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No schedule found with given id")


@router.delete("/schedules/delete/{schedule_id}")
def delete_schedule(schedule_id: str):
    result = schedule_db.delete_schedule(schedule_id)
    if result:
        return {"message": "Schedule deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="schedule not found")


@router.post("/schedules/generate")
def generate_schedule(schedule: Schedule2, background_tasks: BackgroundTasks):
    background_tasks.add_task(_generate_schedule, schedule)
    return {f"message": f"Schedule generation started for {schedule.id}"}


def _generate_schedule(schedule: Schedule2):
    collection_schedules2.delete_many({"id": schedule.id})
    slots = _extract_slots(schedule)
    workers = _extract_workers(schedule)
    try:
        solution = ScheduleSolver(slots, workers).solve()
        solved_schedule = _schedule_from_solution(schedule, solution)
        collection_schedules2.insert_one(solved_schedule.dict(by_alias=True))
        logging.info(f'Generated Schedule for {solved_schedule.id}')
    except NoSolutionFound:
        collection_schedules2.insert_one(schedule=schedule.dict())
        logging.info(f'No solution found for {schedule.id}')


@router.get("/schedules/{schedule_id}", response_model=Schedule2)
def get_schedule(schedule_id: str) -> Schedule2:
    db_schedule = collection_schedules2.find_one({"id": schedule_id})
    if not db_schedule:
        raise HTTPException(status_code=404, detail="No schedule found with given id")
    schedule = Schedule2.parse_obj(db_schedule)
    if not schedule.is_generated:
        raise HTTPException(status_code=404, detail="No solution found for schedule")
    return schedule


def _extract_slots(schedule: Schedule2) -> list[SingleSlot]:
    slots = []
    for day in schedule.days:
        for group in day.groups:
            for slot in group.slots:
                for position in slot.assigned_workers.keys():
                    slots.append(SingleSlot(
                        id=slot.id,
                        start_time=slot.start,
                        end_time=slot.end,
                        group_id=group.id,
                        qualification=position,
                        description=slot.name,
                        pre_scheduled=Operator(*slot.assigned_workers[position])
                        if slot.assigned_workers[position] else None
                    ))
    return slots


def _extract_workers(schedule: Schedule2) -> list[Operator]:
    workers = dict()
    for day in schedule.days:
        for worker in day.workers_data:
            if worker.id not in workers:
                workers[worker.id] = Operator(
                    id=worker.id,
                    name=worker.name,
                    sector=Sector.MIL,
                    qualifications=worker.roles,
                )
            workers[worker.id].requests += worker.requests
            if worker.availability == "Available":
                workers[worker.id].availabilities.append(Availability(start=day.date,
                                                                      end=day.date + timedelta(days=1)))

    return list(workers.values())


def _schedule_from_solution(schedule: Schedule2, solution: list[Placement]) -> Schedule2:
    solved_schedule = deepcopy(schedule)
    for placement in solution:
        found = False
        for day in solved_schedule.days:
            for group in day.groups:
                for slot in group.slots:
                    if slot.id == placement.slot.id:
                        slot.assigned_workers[placement.slot.qualification] = Worker2(
                            id=placement.operator.id,
                            name=placement.operator.name,
                            roles=placement.operator.qualifications,
                            requests=placement.operator.requests,
                            availability="Available"
                        )
                        found = True
        if not found:
            raise Exception(f"Slot not found for placement {placement}")
    solved_schedule.is_generated = True
    return solved_schedule
