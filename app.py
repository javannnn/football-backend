import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# File to store applicants data
DATA_FILE = "applicants.json"

# Static values for QR code and payment
QR_CODE_URL = "https://football-backend-47ii.onrender.com/static/chat_qr_code.jpg"
PHONE_NUMBER = "+251910187397"
AMOUNT_PER_SLOT = 800

# Load applicants data from JSON file
def load_applicants():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save applicants data to JSON file
def save_applicants():
    with open(DATA_FILE, "w") as file:
        json.dump(applicants, file)

# Load applicants at startup
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
    save_applicants()  # Save to JSON file

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
            if updated_slots:
                applicant["slots"] = updated_slots
            if updated_status:
                applicant["status"] = updated_status
            save_applicants()  # Save updates to JSON file
            return jsonify({"message": "Applicant updated successfully"}), 200

    return jsonify({"error": "Applicant not found"}), 404

@app.route('/delete-applicant', methods=['POST'])
def delete_applicant():
    data = request.json
    applicant_id = data.get("id")

    if not applicant_id:
        return jsonify({"error": "Applicant ID is required"}), 400

    global applicants
    applicants = [applicant for applicant in applicants if applicant["id"] != applicant_id]
    save_applicants()  # Save changes to JSON file
    return jsonify({"message": "Applicant deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
