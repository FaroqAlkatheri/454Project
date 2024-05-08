from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import threading
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
socketio = SocketIO(app, cors_allowed_origins='*')  # Allow all CORS origins

# Simulate temperature sensor
def get_temperature():
    return random.randint(20, 30)

# Background task to emit temperature updates
def background_task():
    while True:
        temperature = get_temperature()
        socketio.emit('temperature_update', {'temperature': temperature})
        socketio.sleep(2)  # Update every 2 seconds

# Start the background thread
thread = threading.Thread(target=background_task)
thread.daemon = True
thread.start()

# Route to get initial data
@app.route('/api/temperature', methods=['GET'])
def get_initial_temperature():
    temperature = get_temperature()
    return jsonify({'temperature': temperature})

# Handle socket connections
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    temperature = get_temperature()
    emit('temperature_update', {'temperature': temperature})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)  # Running on port 8080
