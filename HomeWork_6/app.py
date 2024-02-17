#!/usr/bin/env python3


from flask import Flask, jsonify
import uuid

app = Flask(__name__)

@app.route('/healthz')
def health_check():
    # Endpoint for health checks
    return "OK", 200

@app.route('/uuid')
def generate_uuid():
    # Generate a UUID and return it in JSON format
    return jsonify({"uuid": str(uuid.uuid4())})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

