from flask import Flask, jsonify
import uuid

# Create a Flask application instance
app = Flask(__name__)

# Define a route for the root URL
@app.route('/')
def hello():
    # Define a simple JSON response
    data = {
        'message': 'Hello, World!'
    }
    # Return JSON response with Content-Type header set to application/json
    return jsonify(data), 200, {'Content-Type': 'application/json'}

# Define a route for the health check
@app.route('/healthz')
def healthz():
    # Define a simple JSON response indicating the service is healthy
    health_data = {
        'status': 'healthy'
    }
    # Return JSON response with Content-Type header set to application/json
    return jsonify(health_data), 200, {'Content-Type': 'application/json'}


@app.route('/uuid', methods=['GET'])
def get_uuid():
    return jsonify(uuid=str(uuid.uuid4()))

# Run the Flask application
if __name__ == '__main__':
    app.run(port=5001, debug=True)
