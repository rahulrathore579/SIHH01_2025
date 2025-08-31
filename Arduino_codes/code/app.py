from flask import Flask, render_template, jsonify, request
import serial, json, threading, time

# --------- CONFIG ----------
SERIAL_PORT = "COM11"       # ⚠️ Change to your Arduino COM port (Windows: "COM3"/"COM4", Linux: "/dev/ttyUSB0")
BAUD = 9600
# ---------------------------

app = Flask(__name__)

# Global sensor/actuator state
data = {
    "soil_raw": None,
    "soil_pct": None,
    "mq_raw": None,
    "pump": 0,
    "mode": "AUTO",
    "temp_c": None,
    "humid": None,
    "ts": 0
}
last_seen = 0  # timestamp of last valid packet

# ---------------------------
# 🔄 Serial Reader Thread
# ---------------------------
def reader():
    """ Continuously read JSON lines from Arduino """
    global data, last_seen
    while True:
        try:
            print(f"🔌 Connecting to {SERIAL_PORT}...")
            with serial.Serial(SERIAL_PORT, BAUD, timeout=1) as ser:
                ser.reset_input_buffer()
                print("✅ Connected to Arduino")
                while True:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()
                    if not line:
                        continue
                    if line.startswith("{") and line.endswith("}"):
                        try:
                            obj = json.loads(line)
                            data.update(obj)
                            last_seen = time.time()
                            print("📥 Data:", obj)
                        except json.JSONDecodeError:
                            print("⚠️ Invalid JSON:", line)
        except serial.SerialException as e:
            print(f"⚠️ Serial error: {e}. Retrying in 3s...")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}. Retrying in 3s...")
            time.sleep(3)

# Start background thread
threading.Thread(target=reader, daemon=True).start()

# ---------------------------
# 🔧 Serial Command Sender
# ---------------------------
def send_cmd(cmd: str):
    """ Send a command to Arduino over serial """
    try:
        with serial.Serial(SERIAL_PORT, BAUD, timeout=1) as ser:
            ser.write((cmd + "\n").encode("utf-8"))
            print(f"➡️ Sent command: {cmd}")
    except Exception as e:
        print(f"⚠️ Could not send command: {e}")

# ---------------------------
# 🌐 Flask Routes
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    """Return latest Arduino sensor+actuator data as JSON"""
    age = time.time() - last_seen if last_seen else None
    out = dict(data)
    out["age_sec"] = age
    return jsonify(out)

@app.route("/relay/<state>", methods=["POST"])
def relay(state):
    """Turn relay/pump ON or OFF"""
    if state.lower() == "on":
        send_cmd("ON")
    elif state.lower() == "off":
        send_cmd("OFF")
    return ("", 204)

@app.route("/mode/auto", methods=["POST"])
def mode_auto():
    """Set irrigation mode to AUTO"""
    send_cmd("AUTO")
    return ("", 204)

@app.route("/set", methods=["POST"])
def set_thresholds():
    """Set soil moisture thresholds via JSON body"""
    obj = request.get_json(force=True, silent=True) or {}
    if "start" in obj:
        send_cmd(f"SET START {int(obj['start'])}")
    if "stop" in obj:
        send_cmd(f"SET STOP {int(obj['stop'])}")
    return ("", 204)

# ---------------------------
# ▶️ Run Flask
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
