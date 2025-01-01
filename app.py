from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/book', methods=['POST'])
def book_spot():
    data = request.json
    return jsonify({"message": "Booking received", "data": data})

if __name__ == '__main__':
    app.run(debug=True)
