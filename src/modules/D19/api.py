from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
MONGO_URI=os.getenv("MONGO_URI")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Atlas connection
client = MongoClient(MONGO_URI)

db = client["drug_interaction_system"]

drugs_col      = db["drugs"]
interactions_col = db["interactions"]
alternatives_col = db["alternatives"]
alerts_col     = db["alerts"]

print("Connected to MongoDB Atlas")


# --------------------------------------------------
# Get all drugs
# --------------------------------------------------

@app.get("/drugs")
def get_drugs():
    return list(drugs_col.find({}, {"_id": 0}))


# --------------------------------------------------
# Dashboard counts
# --------------------------------------------------

@app.get("/dashboard/counts")
def get_counts():
    return {
        "drugs":        drugs_col.count_documents({}),
        "interactions": interactions_col.count_documents({}),
        "alerts":       alerts_col.count_documents({}),
        "alternatives": alternatives_col.count_documents({}),
    }


# --------------------------------------------------
# Full drug table (all fields)
# --------------------------------------------------
@app.get("/drugs/all")
def get_all_drugs():
    return list(drugs_col.find({}, {"_id": 0}))
# --------------------------------------------------
# Full interactions table
# --------------------------------------------------

@app.get("/interactions/all")
def get_all_interactions():
    return list(interactions_col.find({}, {"_id": 0}).limit(500))


# --------------------------------------------------
# Check drug interaction
# --------------------------------------------------

@app.post("/check-interaction")
def check_interaction(data: dict):
    drug1 = data.get("drug1")
    drug2 = data.get("drug2")

    if not drug1 or not drug2:
        return {"error": "Both drug1 and drug2 are required"}

    result = interactions_col.find_one({
        "$or": [
            {"drug1": drug1, "drug2": drug2},
            {"drug1": drug2, "drug2": drug1}
        ]
    })

    if result:
        alerts_col.insert_one({
            "drug1":     drug1,
            "drug2":     drug2,
            "severity":  result["severity"],
            "mechanism": result.get("mechanism", ""),
            "recommendation": result.get("recommendation", ""),
            "message":   "Drug interaction detected",
            "timestamp": datetime.now()
        })

        return {
            "interaction":    True,
            "severity":       result["severity"],
            "mechanism":      result.get("mechanism", "N/A"),
            "recommendation": result.get("recommendation", "N/A"),
            "message":        "Interaction detected"
        }

    return {
        "interaction": False,
        "message":     "No interaction found"
    }


# --------------------------------------------------
# Get all alerts
# --------------------------------------------------

@app.get("/alerts")
def get_alerts():
    raw = list(alerts_col.find({}, {"_id": 0}))
    for a in raw:
        if "timestamp" in a and hasattr(a["timestamp"], "isoformat"):
            a["timestamp"] = a["timestamp"].isoformat()
    return raw


# --------------------------------------------------
# Get alerts for a specific drug pair
# --------------------------------------------------

@app.get("/alerts/{drug1}/{drug2}")
def get_alerts_for_pair(drug1: str, drug2: str):
    raw = list(alerts_col.find({
        "$or": [
            {"drug1": drug1, "drug2": drug2},
            {"drug1": drug2, "drug2": drug1}
        ]
    }, {"_id": 0}))
    for a in raw:
        if "timestamp" in a and hasattr(a["timestamp"], "isoformat"):
            a["timestamp"] = a["timestamp"].isoformat()
    return raw


# --------------------------------------------------
# Get alternative drug
# --------------------------------------------------

@app.get("/alternatives/{drug}")
def get_alternative(drug: str):
    result = alternatives_col.find_one({"drug": drug}, {"_id": 0})
    if result:
        return result
    return {"message": "No alternative found"}


# --------------------------------------------------
# Severity breakdown for dashboard chart
# --------------------------------------------------

@app.get("/dashboard/severity-breakdown")
def severity_breakdown():
    pipeline = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
    ]
    result = list(interactions_col.aggregate(pipeline))
    return [{"severity": r["_id"], "count": r["count"]} for r in result]


# --------------------------------------------------
# Top drugs involved in interactions
# --------------------------------------------------

@app.get("/dashboard/top-drugs")
def top_drugs():
    pipeline = [
        {"$group": {"_id": "$drug1", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    result = list(interactions_col.aggregate(pipeline))
    return [{"drug": r["_id"], "count": r["count"]} for r in result]
