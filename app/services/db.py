from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
results_collection = db["results"]

def insert_result(result: dict):
    results_collection.insert_one(result)

def fetch_all_results():
    return list(results_collection.find({}, {"_id": 0}))
