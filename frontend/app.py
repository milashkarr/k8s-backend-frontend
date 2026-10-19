import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8080")

@app.route('/')
def index():
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=3)
        return jsonify({
            "frontend": "Hello from FRONTEND! ^-^",
            "backend_response": r.json()
        })
    except Exception as e:
        return jsonify({"frontend": "Hello from FRONTEND! ^-^", "error": str(e)}), 502

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    