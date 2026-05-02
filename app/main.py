from fastapi import FastAPI, Request
from pymongo import MongoClient
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# ✅ CORS (important for frontend / browser access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MongoDB Connection
# Priority: 1. Environment Variable 2. Hardcoded fallback (for dev)
mongo_uri = os.getenv("MONGO_URI", "mongodb://subhajitghoshdev_db_user:test123@ac-ngldqe3-shard-00-00.n3jizes.mongodb.net:27017,ac-ngldqe3-shard-00-01.n3jizes.mongodb.net:27017,ac-ngldqe3-shard-00-02.n3jizes.mongodb.net:27017/?ssl=true&replicaSet=atlas-t6ep8l-shard-0&authSource=admin&appName=Cluster0")

client = MongoClient(mongo_uri)
db = client["aqi_db"]
collection = db["sensor_data"]

def serialize_data(data):
    """Safely convert MongoDB documents to JSON-serializable format"""
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            if k == "_id":
                new_dict[k] = str(v)
            elif isinstance(v, datetime):
                new_dict[k] = v.isoformat()
            else:
                new_dict[k] = v
        return new_dict
    return data

# ✅ Health Check Route
@app.get("/")
def home():
    return {"status": "Working ✅", "service": "Sudh-Vayu API"}

# ✅ Fetch Real-time Data
@app.get("/data")
def get_data():
    try:
        # Fetch latest 50 entries, sorted by most recent if timestamp exists
        cursor = collection.find({}, {"_id": 0}).sort("_id", -1).limit(50)
        data = list(cursor)
        
        return {"data": serialize_data(data)}
    except Exception as e:
        return {"error": str(e), "status": "failed to fetch data"}

# ✅ Receive Sensor Data (Digital Twin Logic)
@app.post("/sensor")
async def receive_data(request: Request):
    try:
        data = await request.json()
        
        # Extract fields with defaults
        co = data.get("co", 0)
        temp = data.get("temp", 0)
        humidity = data.get("humidity", 0)

        # IAQ (Indoor Air Quality) Estimation Logic
        if co < 800:
            iaq = 50
            status = "Good"
        elif co < 1200:
            iaq = 100
            status = "Moderate"
        elif co < 2000:
            iaq = 150
            status = "Unhealthy"
        else:
            iaq = 200
            status = "Hazardous"

        # Derived metrics
        co2_eq = co * 1.5
        alert = "⚠️ High Pollution" if iaq > 150 else "Safe"

        # Prepare enriched document
        enriched_data = {
            "co": co,
            "temp": temp,
            "humidity": humidity,
            "iaq": iaq,
            "co2_eq": co2_eq,
            "status": status,
            "alert": alert,
            "timestamp": datetime.utcnow()
        }

        # Store in MongoDB
        collection.insert_one(enriched_data)

        # Return serializable response
        return {"status": "saved", "data": serialize_data(enriched_data)}

    except Exception as e:
        return {"error": str(e), "status": "failed to save data"}