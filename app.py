import psycopg2
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE_URL = os.getenv("SUPABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
except Exception as e:
    print(f"Database connection failed: {e}")
    exit()

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Football Booking API!"})

@app.route('/book', methods=['POST'])
def book():
    data = request.json
    try:
        cursor.execute(
            "INSERT INTO bookings (name, spots, status) VALUES (%s, %s, %s)",
            (data['name'], data['spots'], 'Pending'),
        )
        conn.commit()
        return jsonify({"message": "Booking received!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
