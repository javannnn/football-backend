import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use the service key for backend operations

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return "Football backend is running!"

@app.route('/applicants', methods=['GET'])
def get_applicants():
    """Fetch all applicants from the database."""
    try:
        response = supabase.table("applicants").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/book', methods=['POST'])
def book_slot():
    """Book a slot for an applicant."""
    data = request.json
    user_name = data.get("name")
    slots = data.get("slots")

    if not user_name or not slots or not isinstance(slots, int) or slots <= 0:
        return jsonify({"error": "Name and a valid number of slots are required"}), 400

    try:
        # Insert applicant into Supabase
        response = supabase.table("applicants").insert({
            "name": user_name,
            "slots": slots,
            "status": "Pending"
        }).execute()
        total_amount = 800 * slots
        return jsonify({
            "message": "Please make your payment to complete the booking.",
            "payment_details": {
                "qr_code": "https://muhkjvufppfapjkoupgc.supabase.co/storage/v1/object/public/static/chat_qr_code.jpg",
                "phone_number": "+251910187397",
                "amount": total_amount
            },
            "applicant_id": response.data[0]["id"]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-applicant', methods=['POST'])
def update_applicant():
    """Update an applicant's details."""
    data = request.json
    applicant_id = data.get("id")
    updated_name = data.get("name")
    updated_slots = data.get("slots")
    updated_status = data.get("status")

    if not applicant_id:
        return jsonify({"error": "Applicant ID is required"}), 400

    try:
        # Update applicant in Supabase
        update_data = {}
        if updated_name:
            update_data["name"] = updated_name
        if updated_slots:
            update_data["slots"] = updated_slots
        if updated_status:
            update_data["status"] = updated_status

        supabase.table("applicants").update(update_data).eq("id", applicant_id).execute()
        return jsonify({"message": "Applicant updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete-applicant', methods=['POST'])
def delete_applicant():
    """Delete an applicant."""
    data = request.json
    applicant_id = data.get("id")

    if not applicant_id:
        return jsonify({"error": "Applicant ID is required"}), 400

    try:
        supabase.table("applicants").delete().eq("id", applicant_id).execute()
        return jsonify({"message": "Applicant deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
