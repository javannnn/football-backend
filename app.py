import psycopg2
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    # Explicitly specify the host for TCP/IP connection
    conn = psycopg2.connect(DATABASE_URL, host='db.muhkjvufppfapjkoupgc.supabase.co')
    cursor = conn.cursor()
    print("Connection successful!")
except psycopg2.Error as e:
    print(f"Connection failed: {e}")

@app.route('/book', methods=['POST'])
def book():
    data = request.json
    cursor.execute("INSERT INTO bookings (name, spots, status) VALUES (%s, %s, %s)",
                   (data['name'], data['spots'], 'Pending'))
    conn.commit()
    return jsonify({"message": "Booking received!"})

if __name__ == '__main__':
    app.run(debug=True)