from fastapi import FastAPI, Request
from pymongo import MongoClient
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from bson import json_util
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MongoDB Connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://subhajitghoshdev_db_user:test123@ac-ngldqe3-shard-00-00.n3jizes.mongodb.net:27017,ac-ngldqe3-shard-00-01.n3jizes.mongodb.net:27017,ac-ngldqe3-shard-00-02.n3jizes.mongodb.net:27017/?ssl=true&replicaSet=atlas-t6ep8l-shard-0&authSource=admin&appName=Cluster0")

client = MongoClient(mongo_uri)
db = client["aqi_db"]
collection = db["sensor_data"]

def parse_json(data):
    """Deeply serialize MongoDB data using bson.json_util"""
    return json.loads(json_util.dumps(data))

# ✅ Health Check Route
@app.get("/")
def home():
    try:
        # Ping the database to check connection
        client.admin.command('ping')
        db_status = "Connected 🚀"
    except Exception as e:
        db_status = f"Connection Failed ❌ ({str(e)})"
        
    return {
        "status": "Working ✅", 
        "database": db_status,
        "service": "Sudh-Vayu API"
    }

# ✅ Fetch Real-time Data
@app.get("/data")
def get_data():
    try:
        # Fetch latest 50 entries
        # Note: We remove _id: 0 here so we can sort by it, and then serialize it to string
        cursor = collection.find().sort("_id", -1).limit(50)
        data = list(cursor)
        
        return {"data": parse_json(data)}
    except Exception as e:
        # If we reach here, return a status code and error message
        return {"error": str(e), "status": "failed to fetch data"}

# ✅ Receive Sensor Data
@app.post("/sensor")
async def receive_data(request: Request):
    try:
        data = await request.json()
        
        co = data.get("co", 0)
        temp = data.get("temp", 0)
        humidity = data.get("humidity", 0)

        # IAQ Logic
        if co < 800:
            iaq, status = 50, "Good"
        elif co < 1200:
            iaq, status = 100, "Moderate"
        elif co < 2000:
            iaq, status = 150, "Unhealthy"
        else:
            iaq, status = 200, "Hazardous"

        enriched_data = {
            "co": co,
            "temp": temp,
            "humidity": humidity,
            "iaq": iaq,
            "co2_eq": co * 1.5,
            "status": status,
            "alert": "⚠️ High Pollution" if iaq > 150 else "Safe",
            "timestamp": datetime.utcnow()
        }

        collection.insert_one(enriched_data)
        return {"status": "saved", "data": parse_json(enriched_data)}

    except Exception as e:
        return {"error": str(e), "status": "failed to save data"}