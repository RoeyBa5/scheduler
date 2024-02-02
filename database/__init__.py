from pymongo import MongoClient
import config

client = MongoClient(f'mongodb+srv://{"ddd"}:{"ddd"}@cluster0.pfk33au.mongodb.net/')
db = client['Scheduler-db']