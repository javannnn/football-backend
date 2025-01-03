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
TELEBIRR_MERCHANT_APP_ID = "1346688522803207"
TELEBIRR_FABRIC_APP_ID = "c4182ef8-9249-458a-985e-06d191f4d505"
TELEBIRR_SHORT_CODE = "484457"
TELEBIRR_APP_SECRET = "fad0f06383c6297f545876694b974599"

# Private key directly embedded here
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/ZcoOng1sJZ4CegopQVCw3HYqq
VRLEudgT+dDpS8fRVy7zBgqZunju2VRCQuHeWs7yWgc9QGd4/8kRSLY+jlvKNeZ60yWcqEY+eKyQM
mcjOz2Sn41fcVNgF+HV3DGiV4b23B6BCMjnpEFIb9d99/TsjsFSc7gCPgfl2yWDxE/Y1B2tVE6op2
qd63YsMVFQGdre/CQYvFJENpQaBLMq4hHyBDgluUXlF0uA1X7UM0ZjbFC6ZIB/Hn1+pl5Ua8dKYrk
VaecolmJT/s7c/+/1JeN+ja8luBoONsoODt2mTeVJHLF9Y3oh5rI+IY8HukIZJ1U6O7/JcjH3aRJT
ZagXUS9AgMBAAECggEBALBIBx8JcWFfEDZFwuAWeUQ7+VX3mVx/770kOuNx24HYt718D/HV0avfKE
THqOfA7AQnz42EF1Yd7Rux1ZO0e3unSVRJhMO4linT1XjJ9ScMISAColWQHk3wY4va/FLPqG7N4L1
w3BBtdjIc0A2zRGLNcFDBlxl/CVDHfcqD3CXdLukm/friX6TvnrbTyfAFicYgu0+UtDvfxTL3pRL3
u3WTkDvnFK5YXhoazLctNOFrNiiIpCW6dJ7WRYRXuXhz7C0rENHyBtJ0zura1WD5oDbRZ8ON4v1KV
4QofWiTFXJpbDgZdEeJJmFmt5HIi+Ny3P5n31WwZpRMHGeHrV23//0CgYEA+2/gYjYWOW3JgMDLX7
r8fGPTo1ljkOUHuH98H/a/lE3wnnKKx+2ngRNZX4RfvNG4LLeWTz9plxR2RAqqOTbX8fj/NA/sS4m
ru9zvzMY1925FcX3WsWKBgKlLryl0vPScq4ejMLSCmypGz4VgLMYZqT4NYIkU2Lo1G1MiDoLy0CcC
gYEAwt77exynUhM7AlyjhAA2wSINXLKsdFFF1u976x9kVhOfmbAutfMJPEQWb2WXaOJQMvMpgg2rU
5aVsyEcuHsRH/2zatrxrGqLqgxaiqPz4ELINIh1iYK/hdRpr1vATHoebOv1wt8/9qxITNKtQTgQbq
Yci3KV1lPsOrBAB5S57nsCgYAvw+cagS/jpQmcngOEoh8I+mXgKEET64517DIGWHe4kr3dO+FFbc5
eZPCbhqgxVJ3qUM4LK/7BJq/46RXBXLvVSfohR80Z5INtYuFjQ1xJLveeQcuhUxdK+95W3kdBBi8l
HtVPkVsmYvekwK+ukcuaLSGZbzE4otcn47kajKHYDQKBgDbQyIbJ+ZsRw8CXVHu2H7DWJlIUBIS3s
+CQ/xeVfgDkhjmSIKGX2to0AOeW+S9MseiTE/L8a1wY+MUppE2UeK26DLUbH24zjlPoI7PqCJjl0D
FOzVlACSXZKV1lfsNEeriC61/EstZtgezyOkAlSCIH4fGr6tAeTU349Bnt0RtvAoGBAObgxjeH6JG
pdLz1BbMj8xUHuYQkbxNeIPhH29CySn0vfhwg9VxAtIoOhvZeCfnsCRTj9OZjepCeUqDiDSoFzngl
rKhfeKUndHjvg+9kiae92iI6qJudPCHMNwP8wMSphkxUqnXFR3lr9A765GA980818UWZdrhrjLKtI
IZdh+X1
-----END PRIVATE KEY-----"""
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
            "notifyUrl": "https://your-backend-url/telebirr-callback",
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
        response = requests.post(
            "https://196.188.120.83:34443/apiaccess/payment/gateway",
            json=payload,
            headers=headers,
            verify=False  # Bypass SSL verification
        )
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
