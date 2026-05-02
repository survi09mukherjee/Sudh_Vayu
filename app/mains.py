from fastapi import FastAPI
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

# ✅ MongoDB Connection (SAFE)
mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    raise Exception("❌ MONGO_URI not set in environment variables")

client = MongoClient(mongo_uri)
db = client["aqi_db"]
collection = db["sensor_data"]


# ✅ Health Check Route
@app.get("/")
def home():
    return {"status": "Working ✅"}


# ✅ Fetch Latest Data (NO CRASH VERSION)
@app.get("/data")
def get_data():
    try:
        data = list(collection.find().limit(5))
        return {"data": str(data)}  # convert to string to avoid crash
    except Exception as e:
        return {"error": str(e)}


# 🧠 DIGITAL TWIN LOGIC
@app.post("/sensor")
def receive_data(data: dict):
    try:
        co = data.get("co", 0)
        temp = data.get("temp", 0)
        humidity = data.get("humidity", 0)

        # 🔥 IAQ estimation
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

        # 🔥 Derived metrics
        co2_eq = co * 1.5
        alert = "⚠️ High Pollution" if iaq > 150 else "Safe"

        # 📦 Store both datetime + string
        enriched_data = {
            "co": co,
            "temp": temp,
            "humidity": humidity,
            "iaq": iaq,
            "co2_eq": co2_eq,
            "status": status,
            "alert": alert,
            "timestamp": datetime.utcnow(),  # for sorting
            "timestamp_str": datetime.utcnow().isoformat()  # for frontend
        }

        collection.insert_one(enriched_data)

        # return safe JSON (no datetime object)
        enriched_data["_id"] = None
        enriched_data["timestamp"] = enriched_data["timestamp_str"]

        return enriched_data

    except Exception as e:
        return {"error": str(e)}