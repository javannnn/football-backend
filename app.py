import psycopg2
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE_URL = os.getenv("SUPABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

@app.route('/book', methods=['POST'])
def book():
    data = request.json
    cursor.execute("INSERT INTO bookings (name, spots, status) VALUES (%s, %s, %s)", 
                   (data['name'], data['spots'], 'Pending'))
    conn.commit()
    return jsonify({"message": "Booking received!"})

if __name__ == '__main__':
    app.run(debug=True)
