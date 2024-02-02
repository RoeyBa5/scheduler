from pymongo import MongoClient
import config as config

client = MongoClient(f'mongodb+srv://{config.MONGODB_USERNAME}:{config.MONGODB_PASSWORD}@cluster0.pfk33au.mongodb.net/')
db = client['Scheduler-db']

collection_schedules = db['schedules']
collection_groups = db['groups']
collection_shifts = db['shifts']
