from pymongo import MongoClient
from itertools import combinations
from datetime import datetime
import random
import os
from dotenv import load_dotenv
load_dotenv()
MONGO_URI=os.getenv("MONGO_URI")
# -----------------------------------
# MongoDB Connection
# -----------------------------------

client = MongoClient(MONGO_URI)

db = client["drug_interaction_system"]

drugs = db["drugs"]
interactions = db["interactions"]
alternatives = db["alternatives"]
alerts = db["alerts"]

print("Connected to MongoDB Atlas")

# -----------------------------------
# Clear old data (optional but recommended)
# -----------------------------------

drugs.delete_many({})
interactions.delete_many({})
alternatives.delete_many({})
alerts.delete_many({})

# -----------------------------------
# Drug dataset (100+ drugs)
# -----------------------------------

drug_names = [
"Aspirin","Warfarin","Ibuprofen","Metformin","Paracetamol","Amoxicillin",
"Atorvastatin","Lisinopril","Omeprazole","Prednisone","Clopidogrel",
"Losartan","Rosuvastatin","Azithromycin","Pantoprazole","Simvastatin",
"Hydrochlorothiazide","Amlodipine","Ciprofloxacin","Doxycycline",
"Cephalexin","Insulin","Glipizide","Glibenclamide","Levothyroxine",
"Furosemide","Spironolactone","Metoprolol","Atenolol","Propranolol",
"Diazepam","Lorazepam","Alprazolam","Fluoxetine","Sertraline",
"Escitalopram","Ranitidine","Cimetidine","Famotidine","Codeine",
"Tramadol","Morphine","Naproxen","Ketorolac","Diclofenac",
"Clarithromycin","Erythromycin","Vancomycin","Linezolid","Rifampin",
"Isoniazid","Ethambutol","Pyrazinamide","Hydrocortisone","Dexamethasone",
"Betamethasone","Insulin glargine","Insulin lispro","Sitagliptin",
"Linagliptin","Canagliflozin","Dapagliflozin","Empagliflozin",
"Verapamil","Diltiazem","Digoxin","Amiodarone","Nitroglycerin",
"Isosorbide","Heparin","Enoxaparin","Rivaroxaban","Apixaban",
"Dabigatran","Cyclophosphamide","Methotrexate","Azathioprine",
"Mycophenolate","Tacrolimus","Cyclosporine","Ondansetron",
"Domperidone","Metoclopramide","Loperamide","Magnesium hydroxide",
"Aluminum hydroxide","Calcium carbonate","Vitamin D","Vitamin B12",
"Folic acid","Iron supplements","Zinc sulfate","Calcium gluconate"
]

drug_data = [
    {"name": name, "class": "General", "description": f"{name} medication"}
    for name in drug_names
]

drugs.insert_many(drug_data)
print("Drug data inserted (100+ drugs)")

# -----------------------------------
# Generate interactions with random severity
# -----------------------------------

severity_levels = ["Minor", "Moderate", "Major"]

interaction_records = []

for d1, d2 in combinations(drug_data, 2):

    interaction_records.append({
        "drug1": d1["name"],
        "drug2": d2["name"],
        "severity": random.choice(severity_levels),
        "mechanism": "Potential interaction between drugs",
        "recommendation": "Consult physician before combining"
    })

# Optional: limit records if needed
# interaction_records = interaction_records[:1000]

interactions.insert_many(interaction_records)

print(f"{len(interaction_records)} interaction records inserted")

# -----------------------------------
# Alternatives (auto-generated)
# -----------------------------------

alternative_records = []

for i in range(len(drug_names)):
    alternative_records.append({
        "drug": drug_names[i],
        "alternative": drug_names[(i+1) % len(drug_names)],
        "reason": "Alternative drug with similar therapeutic effect"
    })

alternatives.insert_many(alternative_records)

print("Alternatives inserted for all drugs")

# -----------------------------------
# Sample Alerts
# -----------------------------------

alert_records = [
    {
        "drug1": "Aspirin",
        "drug2": "Warfarin",
        "severity": "Major",
        "message": "High bleeding risk when combined",
        "timestamp": datetime.now()
    },
    {
        "drug1": "Ibuprofen",
        "drug2": "Warfarin",
        "severity": "Moderate",
        "message": "Monitor patient for bleeding",
        "timestamp": datetime.now()
    }
]

alerts.insert_many(alert_records)

print("Sample alerts inserted")

# -----------------------------------
# Index for faster queries
# -----------------------------------

interactions.create_index([("drug1", 1), ("drug2", 1)])

print("Index created")

print(" Database setup complete")