from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory state
device_state = {
    "led": False,
    "fan": False
}

sensor_data = {
    "temperature": None,
    "light_intensity": None,
    "presence": None
}

@app.route('/')
def home():
    return "Welcome to house IoT system"

# ESP32 sends sensor data here
@app.route('/api/update_sensors', methods=['POST'])
def update_sensors():
    data = request.get_json()
    sensor_data["temperature"] = data.get("temperature")
    sensor_data["light_intensity"] = data.get("light_intensity")
    sensor_data["presence"] = data.get("presence")

    # Automatically control LED based on light level
    if sensor_data["light_intensity"] is not None:
        device_state["led"] = sensor_data["light_intensity"] < 20  # Adjust threshold if needed

    return jsonify({"message": "Sensor data updated"}), 200

# Flask frontend (or anything) can get the latest sensor data
@app.route('/api/temperature', methods=['GET'])
def temperature():
    return jsonify({"temperature": sensor_data["temperature"]}), 200

@app.route('/api/light_intensity', methods=['GET'])
def light_intensity():
    return jsonify({"light_intensity": sensor_data["light_intensity"]}), 200

@app.route('/api/presence', methods=['GET'])
def presence():
    return jsonify({"presence": sensor_data["presence"]}), 200

# Control LED
@app.route('/api/led', methods=['POST'])
def control_led():
    data = request.get_json()
    state = data.get("state")
    if isinstance(state, bool):
        device_state["led"] = state
        return jsonify({"led": device_state["led"]}), 200
    return jsonify({"error": "Invalid LED state"}), 400

# Control Fan
@app.route('/api/fan', methods=['POST'])
def control_fan():
    data = request.get_json()
    state = data.get("state")
    if isinstance(state, bool):
        device_state["fan"] = state
        return jsonify({"fan": device_state["fan"]}), 200
    return jsonify({"error": "Invalid fan state"}), 400

# ESP32 can GET this to know whether to turn LED/fan on or off
@app.route('/api/devices', methods=['GET'])
def get_device_states():
    return jsonify(device_state), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=False)
