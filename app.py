import psycopg2
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

DATABASE_URL = os.getenv("SUPABASE_URL")

# Database connection setup
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
except Exception as e:
    print(f"Database connection failed: {e}")
    exit()

# Default route
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Football Booking API!"})


# Fetch all applicants (GET /applicants)
@app.route('/applicants', methods=['GET'])
def get_applicants():
    try:
        cursor.execute("SELECT id, name, spots, status FROM bookings")
        applicants = cursor.fetchall()
        return jsonify([
            {"id": row[0], "name": row[1], "spots": row[2], "status": row[3]}
            for row in applicants
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update applicant status (PUT /applicants/:id)
@app.route('/applicants/<int:applicant_id>', methods=['PUT'])
def update_status(applicant_id):
    data = request.json
    new_status = data.get('status')
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
    try:
        cursor.execute(
            "UPDATE bookings SET status = %s WHERE id = %s",
            (new_status, applicant_id)
        )
        conn.commit()
        return jsonify({"message": "Status updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Book a spot (POST /book)
@app.route('/book', methods=['POST'])
def book():
    data = request.json
    try:
        # Check if 20 confirmed spots are already taken
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Paid'")
        confirmed_count = cursor.fetchone()[0]
        if confirmed_count >= 20:
            return jsonify({"error": "No more spots available"}), 400

        # Insert the new booking
        cursor.execute(
            "INSERT INTO bookings (name, spots, status) VALUES (%s, %s, %s)",
            (data['name'], data['spots'], 'Pending')
        )
        conn.commit()
        return jsonify({"message": "Booking received! Please confirm payment."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
