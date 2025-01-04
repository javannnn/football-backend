import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Constants
QR_CODE_URL = "https://football-backend-47ii.onrender.com/static/chat_qr_code.jpg"
PHONE_NUMBER = "+251910187397"
AMOUNT_PER_SLOT = 800

@app.route('/')
def home():
    return "Football backend is running!"

@app.route('/applicants', methods=['GET'])
def get_applicants():
    """Fetch all applicants from Supabase."""
    result = supabase.table("applicants").select("*").execute()
    if result.get("error"):
        return jsonify({"error": result["error"]["message"]}), 400
    return jsonify(result.data)

@app.route('/book', methods=['POST'])
def book_slot():
    """Book a slot and save to Supabase."""
    data = request.json
    user_name = data.get("name")
    slots = data.get("slots")

    if not user_name or not slots or not isinstance(slots, int) or slots <= 0:
        return jsonify({"error": "Name and a valid number of slots are required"}), 400

    total_amount = AMOUNT_PER_SLOT * slots

    # Insert into Supabase
    result = supabase.table("applicants").insert({
        "name": user_name,
        "slots": slots,
        "status": "Pending"
    }).execute()

    if result.get("error"):
        return jsonify({"error": result["error"]["message"]}), 400

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
    """Update an applicant's details in Supabase."""
    data = request.json
    applicant_id = data.get("id")
    updated_name = data.get("name")
    updated_spots = data.get("slots")
    updated_status = data.get("status")

    if not applicant_id:
        return jsonify({"error": "Applicant ID is required"}), 400

    updates = {}
    if updated_name:
        updates["name"] = updated_name
    if updated_spots is not None:
        updates["slots"] = updated_spots
    if updated_status:
        updates["status"] = updated_status

    result = supabase.table("applicants").update(updates).eq("id", applicant_id).execute()
    if result.get("error"):
        return jsonify({"error": result["error"]["message"]}), 400

    if len(result.data) == 0:
        return jsonify({"error": "Applicant not found"}), 404

    return jsonify({"message": "Applicant updated successfully"}), 200

@app.route('/delete-applicant', methods=['POST'])
def delete_applicant():
    """Delete an applicant from Supabase."""
    data = request.json
    applicant_id = data.get("id")

    if not applicant_id:
        return jsonify({"error": "Applicant ID is required"}), 400

    result = supabase.table("applicants").delete().eq("id", applicant_id).execute()
    if result.get("error"):
        return jsonify({"error": result["error"]["message"]}), 400

    return jsonify({"message": "Applicant deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
