import network
import urequests as requests
import machine
import time

# Sensor and actuator pins
pir = machine.Pin(5, machine.Pin.IN)
ldr = machine.ADC(machine.Pin(35))
ldr.atten(machine.ADC.ATTN_11DB)  # 0–2.0V range

led = machine.Pin(21, machine.Pin.OUT)
fan = machine.Pin(19, machine.Pin.OUT)

led.value(0)
fan.value(1)  # Fan off (active-low)

# Pushbutton on D33
button = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP)
last_button_state = 1
last_toggle_time = time.ticks_ms()
fan_state = False  # Starts off

SSID = 'MPUNGUTYEASUS 2543'
PASSWORD = '6$8Vt657'
FLASK_SERVER = 'http://172.16.35.144:5000'

def connect_wifi(timeout=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(SSID, PASSWORD)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                print('Wi-Fi connection timeout')
                return False
            time.sleep(1)
    print('Connected to WiFi:', wlan.ifconfig())
    return True

def ping_server():
    try:
        res = requests.get(FLASK_SERVER + '/')
        print("Pinging server...")
        print("Server responded with:", res.status_code)
        res.close()
        return True
    except Exception as e:
        print("Ping failed:", e)
        return False

def read_light():
    try:
        raw = ldr.read()
        percent = int((raw / 4095) * 100)
        print("Light Intensity:", percent, "%")
        return percent
    except Exception as e:
        print("LDR read error:", e)
        return None

def read_motion():
    try:
        motion = pir.value()
        print("Motion Detected:", "Yes" if motion else "No")
        return motion
    except Exception as e:
        print("PIR read error:", e)
        return None

def send_data(light, motion, temperature=None):
    payload = {
        "light_intensity": light,
        "presence": bool(motion)
    }
    if temperature is not None:
        payload["temperature"] = temperature

    try:
        res = requests.post(FLASK_SERVER + "/api/update_sensors", json=payload)
        print("Data sent, status:", res.status_code)
        res.close()
    except Exception as e:
        print("Send Error:", e)

def update_actuators():
    try:
        res = requests.get(FLASK_SERVER + "/api/devices")
        if res.status_code == 200:
            data = res.json()
            print("Fetched device state from server:", data)
            led.value(1 if data.get("led") else 0)
            fan.value(0 if data.get("fan") else 1)  # active-low fan
        res.close()
    except Exception as e:
        print("Actuator update error:", e)

# Main loop
if connect_wifi():
    if ping_server():
        while True:
            try:
                light = read_light()
                motion = read_motion()

                # Check button for fan toggle
                current_button_state = button.value()
                if current_button_state == 0 and last_button_state == 1:
                    if time.ticks_diff(time.ticks_ms(), last_toggle_time) > 300:
                        fan_state = not fan_state
                        fan.value(0 if fan_state else 1)  # active-low
                        print("Fan toggled", "ON" if fan_state else "OFF")
                        last_toggle_time = time.ticks_ms()
                last_button_state = current_button_state

                # Simulated temperature when fan is on
                temperature = 30 if fan_state else None

                if light is not None and motion is not None:
                    send_data(light, motion, temperature)
                else:
                    print("Skipping send due to missing data.")

                update_actuators()

            except Exception as e:
                print("General Loop Error:", e)

            time.sleep(0.1)
    else:
        print("Server not reachable.")
else:
    print("Wi-Fi failed. Restart device.")
