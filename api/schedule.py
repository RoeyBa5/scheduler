from copy import deepcopy
from datetime import timedelta
from typing import List

from fastapi import HTTPException
from fastapi.responses import JSONResponse

import repository.schedule as schedule_db
from api import router
from models.models import Schedule, Schedule2, Worker2
from solver.schedule_solver import ScheduleSolver
from solver.temp_models import SingleSlot, Qualification, Operator, Availability, Sector, Placement


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


@router.get("/schedules/{schedule_id}", response_model=Schedule)
def get_schedule(schedule_id: str):
    result = schedule_db.get_schedule(schedule_id)
    if result:
        return JSONResponse(content=result, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="No schedules found")


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


@router.post("/schedules/generate/{schedule_id}")
def generate_schedule(schedule: Schedule2) -> Schedule2:
    slots = _extract_slots(schedule)
    workers = _extract_workers(schedule)
    solution = ScheduleSolver(slots, workers).solve()
    return _schedule_from_solution(schedule, solution)


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
                        qualification=Qualification(position),
                        description=slot.name,
                        pre_scheduled=slot.assigned_workers[position]
                    ))
    return slots


def _extract_workers(schedule: Schedule2) -> list[Operator]:
    workers = dict()
    for day in schedule.days:
        for worker in day.workersData:
            if worker.id not in workers:
                workers[worker.id] = Operator(
                    id=worker.id,
                    name=worker.name,
                    sector=Sector.MIL,
                    qualifications=worker.roles,
                )
            workers[worker.id].requests.update(worker.requests)
            if worker.availability == "Available":
                workers[worker.id].availabilities.append(Availability(start=day.date,
                                                                      end=day.date + timedelta(days=1)))

    return list(workers.values())


def _schedule_from_solution(schedule: Schedule2, solution: list[Placement]) -> Schedule2:
    solved_schedule = deepcopy(schedule)
    for placement in solution:
        slot = next((day.groups for day in solved_schedule.days for group in day.groups
                     for slot in group.slots if slot.id == placement.slot.id), None)
        if not slot:
            raise Exception(f"Slot not found for placement {placement}")
        slot.assigned_workers[placement.operator.qualifications] = Worker2(
            id=placement.operator.id,
            name=placement.operator.name,
            roles=placement.operator.qualifications,
            requests=placement.operator.requests,
            availability="Available"
        )
    return solved_schedule
