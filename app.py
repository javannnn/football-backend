import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Files to store applicants data and final teams
DATA_FILE = "applicants.json"
FINAL_TEAMS_FILE = "final_teams.json"

# Static values for QR code and payment
QR_CODE_URL = "https://football-backend-47ii.onrender.com/static/chat_qr_code.jpg"
PHONE_NUMBER = "+251910187397"
AMOUNT_PER_SLOT = 800

# Hardcoded applicants (used if applicants.json is missing or invalid)
HARDCODED_APPLICANTS = [
    {"id": 1, "name": "Yafet Surafel", "slots": 1, "status": "Paid"},
    {"id": 2, "name": "Azarias Berhan", "slots": 1, "status": "Paid"},
    {"id": 3, "name": "Minilik", "slots": 1, "status": "Paid"},
    {"id": 4, "name": "Samuel Adamu", "slots": 1, "status": "Paid"},
    {"id": 5, "name": "Bernabas Dinberu", "slots": 1, "status": "Paid"},
    {"id": 6, "name": "Abraham Teklay", "slots": 1, "status": "Paid"},
    {"id": 7, "name": "Zelalem Gashaw", "slots": 1, "status": "Paid"},
    {"id": 8, "name": "Samuel Tesfaye", "slots": 1, "status": "Paid"},
    {"id": 9, "name": "Degneh Dinberu", "slots": 1, "status": "Paid"},
    {"id": 10, "name": "Eyuel Girma", "slots": 1, "status": "Paid"},
    {"id": 11, "name": "Eyuel Teferi", "slots": 1, "status": "Paid"},
    {"id": 12, "name": "Solomon Girma", "slots": 1, "status": "Paid"},
    {"id": 13, "name": "Natty Bekele", "slots": 1, "status": "Paid"},
    {"id": 14, "name": "Micky Bekele", "slots": 1, "status": "Paid"},
    {"id": 15, "name": "Samuel bmp", "slots": 1, "status": "Paid"},
    {"id": 16, "name": "Eyosias Belay", "slots": 1, "status": "Paid"},
    {"id": 17, "name": "Mitiku", "slots": 1, "status": "Paid"},
    {"id": 18, "name": "Elnatan Tesfaw", "slots":1, "status":"Paid"},
]

def load_applicants():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        save_applicants(HARDCODED_APPLICANTS)
        return HARDCODED_APPLICANTS

def save_applicants(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def load_final_teams():
    try:
        with open(FINAL_TEAMS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_final_teams(data):
    with open(FINAL_TEAMS_FILE, "w") as file:
        json.dump(data, file, indent=4)

applicants = load_applicants()

@app.route('/')
def home():
    return "Football backend is running!"

@app.route('/applicants', methods=['GET'])
def get_applicants():
    return jsonify(applicants)

@app.route('/book', methods=['POST'])
def book_slot():
    data = request.json
    user_name = data.get("name")
    slots = data.get("slots")

    if not user_name or not slots or not isinstance(slots, int) or slots <= 0:
        return jsonify({"error": "Name and a valid number of slots are required"}), 400

    total_amount = AMOUNT_PER_SLOT * slots
    applicant = {
        "id": len(applicants) + 1,
        "name": user_name,
        "slots": slots,
        "status": "Pending"
    }
    applicants.append(applicant)
    save_applicants(applicants)

    return jsonify({
        "message": "Please make your payment to complete the booking.",
        "payment_details": {
            "qr_code": QR_CODE_URL,
            "phone_number": PHONE_NUMBER,
            "amount": total_amount
        }
    })

@app.route('/update-applicant', methods=['POST'])
def update_applicant():
    data = request.json
    applicant_id = data.get("id")
    updated_name = data.get("name")
    updated_slots = data.get("slots")
    updated_status = data.get("status")

    if not applicant_id:
        return jsonify({"error": "Applicant ID is required"}), 400

    for applicant in applicants:
        if applicant["id"] == applicant_id:
            if updated_name:
                applicant["name"] = updated_name
            if updated_slots is not None:
                applicant["slots"] = updated_slots
            if updated_status:
                applicant["status"] = updated_status
            save_applicants(applicants)
            return jsonify({"message": "Applicant updated successfully"}), 200

    return jsonify({"error": "Applicant not found"}), 404

@app.route('/delete-applicant', methods=['POST'])
def delete_applicant():
    data = request.json
    applicant_id = data.get("id")

    if not applicant_id:
        return jsonify({"error": "Applicant ID is required"}), 400

    global applicants
    applicants = [app for app in applicants if app["id"] != applicant_id]
    save_applicants(applicants)
    return jsonify({"message": "Applicant deleted successfully"}), 200

# New endpoints to handle final teams
@app.route('/get-teams', methods=['GET'])
def get_teams():
    final_teams = load_final_teams()
    return jsonify(final_teams)

@app.route('/save-teams', methods=['POST'])
def save_teams():
    data = request.json  # This should be the array of teams (plus leftover if needed)
    if not data or not isinstance(data, list):
        return jsonify({"error": "Invalid teams data"}), 400
    save_final_teams(data)
    return jsonify({"message": "Teams saved successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
