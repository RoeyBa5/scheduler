import os

from bson import ObjectId
from fastapi import HTTPException
from pymongo import MongoClient

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')

client = MongoClient(f'mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster0.pfk33au.mongodb.net/')
db = client['Scheduler-db']

collection_operators = db['operators']
collection_schedules = db['schedules']
collection_schedules2 = db['schedules2']
collection_groups = db['groups']
collection_shifts = db['shifts']
collection_availabilities = db['availabilities']
collection_requests = db['requests']


def object_id(obj_id: str):
    try:
        return ObjectId(obj_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Error - ObjectID is invalid")


def execute_db(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Database error: {e}")
