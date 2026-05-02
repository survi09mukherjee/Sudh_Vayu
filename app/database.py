from pymongo import MongoClient
import os

MONGO_URI = "your_mongodb_connection_string_here"

client = MongoClient(MONGO_URI)
db = client["aqi_db"]
collection = db["sensor_data"]