from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime

app = FastAPI()

client = MongoClient(os.getenv"MONGO_URI")
db = client["aqi_db"]
collection = db["sensor_data"]

@app.get("/")
def home():
    return {"status": "Working ✅"}

@app.get("/data")
def get_data():
    return list(collection.find({}, {"_id": 0}).limit(50))


# 🧠 DIGITAL TWIN LOGIC
@app.post("/sensor")
def receive_data(data: dict):

    co = data.get("co", 0)
    temp = data.get("temp", 0)
    humidity = data.get("humidity", 0)

    # 🔥 IAQ estimation (basic model)
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

    # 🔥 CO2 equivalent (approximation)
    co2_eq = co * 1.5

    # 🔥 Risk logic
    if iaq > 150:
        alert = "⚠️ High Pollution"
    else:
        alert = "Safe"

    # 📦 Final enriched data
    enriched_data = {
        "co": co,
        "temp": temp,
        "humidity": humidity,
        "iaq": iaq,
        "co2_eq": co2_eq,
        "status": status,
        "alert": alert,
        "timestamp": datetime.now()
    }

    collection.insert_one(enriched_data)

    print("Stored:", enriched_data)

    return enriched_data