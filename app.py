import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Static values for QR code and payment
QR_CODE_URL = "https://football-backend-47ii.onrender.com/static/chat_qr_code.jpg"
PHONE_NUMBER = "+251910187397"
AMOUNT_PER_SLOT = 800

# Applicants data
applicants = []
applicant_id_counter = 1  # Counter to generate unique IDs for applicants

@app.route('/')
def home():
    return "Football backend is running!"

@app.route('/applicants', methods=['GET'])
def get_applicants():
    """Get the list of applicants."""
    return jsonify(applicants)

@app.route('/book', methods=['POST'])
def book_slot():
    """Book a slot and calculate the payment."""
    global applicant_id_counter

    data = request.json
    user_name = data.get("name")
    slots = data.get("slots")

    # Validate input
    if not user_name or not slots or not isinstance(slots, int) or slots <= 0:
        return jsonify({"error": "Name and a valid number of slots are required"}), 400

    # Calculate total amount
    total_amount = AMOUNT_PER_SLOT * slots

    # Save applicant data
    applicant = {
        "id": applicant_id_counter,
        "name": user_name,
        "slots": slots,
        "status": "Pending"
    }
    applicants.append(applicant)
    applicant_id_counter += 1

    return jsonify({
        "message": "Please make your payment to complete the booking.",
        "payment_details": {
            "qr_code": QR_CODE_URL,
            "phone_number": PHONE_NUMBER,
            "amount": total_amount
        }
    })

@app.route('/update-status', methods=['POST'])
def update_status():
    """Update the status of an applicant."""
    data = request.json
    applicant_id = data.get("id")
    new_status = data.get("status")

    if not applicant_id or not new_status:
        return jsonify({"error": "Applicant ID and status are required"}), 400

    for applicant in applicants:
        if applicant["id"] == applicant_id:
            applicant["status"] = new_status
            return jsonify({"message": "Status updated successfully"}), 200

    return jsonify({"error": "Applicant not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
