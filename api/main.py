from fastapi import FastAPI

from app.api import operators, trainings, schedule, groups

app = FastAPI()

app.include_router(operators.router, tags=["operators"])
app.include_router(trainings.router, tags=["trainings"])
app.include_router(schedule.router, tags=["schedules"])
app.include_router(groups.router, tags=["groups"])
