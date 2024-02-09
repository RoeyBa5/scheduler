import os

from pymongo import MongoClient
import config as config
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')

client = MongoClient(f'mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster0.pfk33au.mongodb.net/')
db = client['Scheduler-db']

collection_operators = db['operators']
collection_schedules = db['schedules']
collection_groups = db['groups']
collection_shifts = db['shifts']
collection_availabilities = db['availabilities']
collection_requests = db['requests']
