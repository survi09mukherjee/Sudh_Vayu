from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()

# 🔥 paste your connection string here
client = MongoClient("mongodb://subhajitghoshdev_db_user:test123@ac-ngldqe3-shard-00-00.n3jizes.mongodb.net:27017,ac-ngldqe3-shard-00-01.n3jizes.mongodb.net:27017,ac-ngldqe3-shard-00-02.n3jizes.mongodb.net:27017/?ssl=true&replicaSet=atlas-t6ep8l-shard-0&authSource=admin&appName=Cluster0")

db = client["aqi_db"]
collection = db["sensor_data"]

@app.get("/")
def home():
    return {"status": "Working ✅"}
@app.get("/data")
def get_data():
    return list(collection.find({}, {"_id": 0}).limit(50))

@app.post("/sensor")
def receive_data(data: dict):
    collection.insert_one(data)   # 🔥 store data

    print("Stored:", data)

    return {"status": "saved"}