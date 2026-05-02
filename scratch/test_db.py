from pymongo import MongoClient
import json

uri = "mongodb://subhajitghoshdev_db_user:test123@ac-ngldqe3-shard-00-00.n3jizes.mongodb.net:27017,ac-ngldqe3-shard-00-01.n3jizes.mongodb.net:27017,ac-ngldqe3-shard-00-02.n3jizes.mongodb.net:27017/?ssl=true&replicaSet=atlas-t6ep8l-shard-0&authSource=admin&appName=Cluster0"

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client["aqi_db"]
    collection = db["sensor_data"]
    
    print("Connecting to MongoDB...")
    count = collection.count_documents({})
    print(f"Total documents: {count}")
    
    data = list(collection.find({}, {"_id": 0}).limit(5))
    print("Sample data:")
    print(data)
    
except Exception as e:
    print(f"Error: {e}")
