import os
import json
import base64
import time
import hashlib
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Telebirr credentials
TELEBIRR_MERCHANT_APP_ID = os.getenv("TELEBIRR_MERCHANT_APP_ID")
TELEBIRR_FABRIC_APP_ID = os.getenv("TELEBIRR_FABRIC_APP_ID")
TELEBIRR_SHORT_CODE = os.getenv("TELEBIRR_SHORT_CODE")
TELEBIRR_APP_SECRET = os.getenv("TELEBIRR_APP_SECRET")
PRIVATE_KEY = os.getenv("TELEBIRR_PRIVATE_KEY")

# Telebirr endpoints
INITIATE_PAYMENT_URL = "https://openapi.ethiotelecom.et/paymentService/open-payment"  # Replace with actual Telebirr endpoint

# Load private key
private_key = serialization.load_pem_private_key(
    PRIVATE_KEY.encode(),
    password=None,
)

@app.route('/book', methods=['POST'])
def initiate_payment():
    data = request.json
    user_name = data.get("name")
    user_phone = data.get("phone")
    amount = 800  # Fixed amount for booking

    if not user_name or not user_phone:
        return jsonify({"error": "Name and phone number are required"}), 400

    try:
        # Prepare payment payload
        payload = {
            "outTradeNo": f"booking-{int(time.time())}",
            "subject": "Yerer Football Booking",
            "totalAmount": amount,
            "notifyUrl": "https://your-backend-url/telebirr-notify",
            "shortCode": TELEBIRR_SHORT_CODE,
            "timeoutExpress": "30m",
            "appId": TELEBIRR_MERCHANT_APP_ID,
            "receiveName": user_name,
            "returnUrl": "https://your-frontend-url/booking-success",
            "callbackUrl": "https://your-backend-url/telebirr-callback"
        }

        # Generate signature
        serialized_payload = json.dumps(payload, separators=(',', ':'))
        hashed_payload = hashlib.sha256(serialized_payload.encode()).digest()
        signature = private_key.sign(
            hashed_payload,
            padding.PKCS1v15(),
            SHA256()
        )
        signed_signature = base64.b64encode(signature).decode()

        # Add signature to payload
        payload["sign"] = signed_signature

        # Send payment request
        headers = {"Content-Type": "application/json"}
        response = requests.post(INITIATE_PAYMENT_URL, json=payload, headers=headers)
        response_data = response.json()

        if response_data.get("code") == "200":
            return jsonify({"message": "Payment initiated successfully", "data": response_data})
        else:
            return jsonify({"error": response_data.get("message", "Payment initiation failed")}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/telebirr-callback', methods=['POST'])
def handle_payment_callback():
    # Process callback data from Telebirr to confirm payment status
    callback_data = request.json
    # Validate and process the callback (e.g., mark booking as paid)
    return jsonify({"message": "Callback received", "data": callback_data})

if __name__ == '__main__':
    app.run(debug=True)
