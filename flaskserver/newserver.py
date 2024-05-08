from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import threading
import paho.mqtt.client as mqtt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
socketio = SocketIO(app, cors_allowed_origins='*')

# MQTT Configuration
MQTT_BROKER = 'your_mqtt_broker_address'  # MQTT broker address
MQTT_PORT = 1883  # Default MQTT port

# MQTT topics
TEMPERATURE_TOPIC = 'temperature/data'  # Topic for temperature data
HUMIDITY_TOPIC = 'humidity/data'  # Topic for humidity data
LIGHT_CONTROL_TOPIC = 'light/control'  # Topic to publish RGB values for light control
DO_NOT_DISTURB_TOPIC = 'user/dnd'  # Topic for "Do Not Disturb"

mqtt_client = mqtt.Client()

# Handle MQTT connection
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    # Subscribe to temperature and humidity topics
    client.subscribe(TEMPERATURE_TOPIC)
    client.subscribe(HUMIDITY_TOPIC)

# Handle incoming MQTT messages
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == TEMPERATURE_TOPIC:
        socketio.emit('temperature_update', {'temperature': payload})
    elif topic == HUMIDITY_TOPIC:
        socketio.emit('humidity_update', {'humidity': payload})

# Background MQTT task
def mqtt_background_task():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Connect to the MQTT broker
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_forever()  # Keep the MQTT client running in a loop

# Start the MQTT background thread
mqtt_thread = threading.Thread(target=mqtt_background_task)
mqtt_thread.daemon = True
mqtt_thread.start()

# REST API for light control (POST RGB values)
@app.route('/api/light_control', methods=['POST'])
def light_control():
    data = request.get_json()
    rgb = data.get('rgb', '0,0,0')  # Default to black if no RGB values are provided
    print(f"Received RGB values for light control: {rgb}")
    mqtt_client.publish(LIGHT_CONTROL_TOPIC, rgb)
    return jsonify({'status': 'success', 'rgb': rgb})

# REST API for "Do Not Disturb" (POST command)
@app.route('/api/do_not_disturb', methods=['POST'])
def do_not_disturb():
    print("Received 'Do Not Disturb' command")
    mqtt_client.publish(DO_NOT_DISTURB_TOPIC, 'do_not_disturb')
    return jsonify({'status': 'success'})

# Run the Flask-SocketIO server
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)
