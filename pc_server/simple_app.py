#!/usr/bin/env python3
"""
Plant Disease Detection & Sprinkler Control - PC Master Controller
PC captures images, runs AI detection, makes decisions, and controls Pi
"""

from flask import Flask, jsonify, render_template, request
import os
import cv2
import time
import json
from datetime import datetime
import requests
import numpy as np

# Import detection module
from detection import detect_disease

# Create Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Global variables to store recent results
recent_detections = []
recent_actions = []

# Configuration
app.config.update(
    SECRET_KEY="dev-secret-key",
    GEMINI_API_KEY="AIzaSyDHW3ArABy2ogwl7twkVXT0oqDR4ykioxw",
    GEMINI_MODEL="gemini-2.0-flash-exp",
    SEVERITY_LOW_THRESHOLD=30.0,
    SEVERITY_HIGH_THRESHOLD=70.0,
    SPRAY_DURATION_LOW_MS=2000,
    SPRAY_DURATION_HIGH_MS=5000,
    # Pi Configuration
    PI_API_URL="http://10.203.228.43:5001/sprinkle",  # Change to your Pi's IP
    PI_TIMEOUT=10,
)

# Camera configuration
camera = None
is_camera_running = False

@app.route('/')
def index():
    return render_template(
        "index.html",
        detections=recent_detections[-10:],  # Show last 10 detections
        actions=recent_actions[-10:],        # Show last 10 actions
        low=app.config["SEVERITY_LOW_THRESHOLD"],
        high=app.config["SEVERITY_HIGH_THRESHOLD"],
    )

@app.route('/api/capture_and_detect', methods=['POST'])
def capture_and_detect():
    """Capture image, detect disease, make decision, and control Pi"""
    try:
        # Step 1: Capture Image
        image = capture_image()
        if image is None:
            return jsonify({"error": "Failed to capture image", "status": "error"}), 500
        
        # Save image temporarily
        timestamp = int(time.time())
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join("temp", filename)
        
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Save captured image
        cv2.imwrite(filepath, image)
        
        # Step 2: AI Disease Detection
        disease, severity, data = detect_disease(filepath)
        
        # Step 3: Decision Logic
        if severity > app.config["SEVERITY_HIGH_THRESHOLD"]:
            action = "on"
            duration_ms = app.config["SPRAY_DURATION_HIGH_MS"]
            result = "Diseased (High)"
        elif severity > app.config["SEVERITY_LOW_THRESHOLD"]:
            action = "on"
            duration_ms = app.config["SPRAY_DURATION_LOW_MS"]
            result = "Diseased (Low)"
        else:
            action = "off"
            duration_ms = 0
            result = "Healthy"
        
        # Step 4: Send Command to Pi
        pi_response = send_command_to_pi(action, duration_ms)
        
        # Step 5: Store Results
        detection_result = {
            "id": len(recent_detections) + 1,
            "disease": disease,
            "severity": severity,
            "result": result,
            "action": action,
            "duration_ms": duration_ms,
            "pi_response": pi_response,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_path": filename
        }
        
        action_result = {
            "id": len(recent_actions) + 1,
            "action": action,
            "duration_ms": duration_ms,
            "severity": severity,
            "pi_status": pi_response.get("status", "unknown"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        recent_detections.append(detection_result)
        recent_actions.append(action_result)
        
        # Keep only last 50 results
        if len(recent_detections) > 50:
            recent_detections.pop(0)
        if len(recent_actions) > 50:
            recent_actions.pop(0)
        
        # Clean up temp file
        try:
            os.remove(filepath)
        except:
            pass
        
        response_data = {
            "status": "success",
            "result": result,
            "disease": disease,
            "severity": severity,
            "action": action,
            "duration_ms": duration_ms,
            "pi_response": pi_response,
            "timestamp": datetime.now().isoformat(),
            "detection_id": detection_result["id"]
        }
        
        # Log the complete cycle
        print(f"🌱 Complete Cycle: {result} - Disease: {disease} - Severity: {severity}% - Action: {action} - Duration: {duration_ms}ms")
        print(f"📡 Pi Response: {pi_response}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in capture and detect cycle: {str(e)}")
        return jsonify({
            "error": f"Detection failed: {str(e)}",
            "status": "error"
        }), 500

def capture_image():
    """Capture image from camera"""
    global camera, is_camera_running
    
    try:
        if not is_camera_running:
            # Initialize camera
            camera = cv2.VideoCapture(0)  # Use default camera
            if not camera.isOpened():
                print("❌ Failed to open camera")
                return None
            
            # Set camera properties
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 15)
            is_camera_running = True
            print("✅ Camera initialized")
        
        # Capture frame
        ret, frame = camera.read()
        if not ret:
            print("❌ Failed to capture frame")
            return None
        
        return frame
        
    except Exception as e:
        print(f"❌ Camera error: {e}")
        return None

def send_command_to_pi(action, duration_ms):
    """Send command to Raspberry Pi"""
    try:
        payload = {
            "action": action,
            "duration": duration_ms
        }
        
        response = requests.post(
            app.config["PI_API_URL"],
            json=payload,
            timeout=app.config["PI_TIMEOUT"]
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Pi API error: {response.status_code} - {response.text}")
            return {"status": "error", "message": f"Pi API error: {response.status_code}"}
            
    except requests.exceptions.Timeout:
        print("❌ Pi API timeout")
        return {"status": "timeout", "message": "Pi API timeout"}
    except requests.exceptions.ConnectionError:
        print("❌ Pi API connection error")
        return {"status": "connection_error", "message": "Cannot connect to Pi"}
    except Exception as e:
        print(f"❌ Pi API error: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/api/start_camera', methods=['POST'])
def start_camera():
    """Start camera for continuous monitoring"""
    global camera, is_camera_running
    
    try:
        if not is_camera_running:
            camera = cv2.VideoCapture(0)
            if camera.isOpened():
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                camera.set(cv2.CAP_PROP_FPS, 15)
                is_camera_running = True
                print("✅ Camera started")
                return jsonify({"status": "success", "message": "Camera started"})
            else:
                return jsonify({"status": "error", "message": "Failed to start camera"}), 500
        else:
            return jsonify({"status": "success", "message": "Camera already running"})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    """Stop camera"""
    global camera, is_camera_running
    
    try:
        if camera and is_camera_running:
            camera.release()
            camera = None
            is_camera_running = False
            print("✅ Camera stopped")
            return jsonify({"status": "success", "message": "Camera stopped"})
        else:
            return jsonify({"status": "success", "message": "Camera already stopped"})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "camera_running": is_camera_running,
        "detections_count": len(recent_detections),
        "actions_count": len(recent_actions),
        "pi_api_url": app.config["PI_API_URL"]
    })

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get recent results for UI updates"""
    return jsonify({
        "detections": recent_detections[-10:],
        "actions": recent_actions[-10:],
        "total_detections": len(recent_detections),
        "total_actions": len(recent_actions)
    })

@app.route('/api/test_pi_connection', methods=['POST'])
def test_pi_connection():
    """Test connection to Raspberry Pi"""
    try:
        response = requests.get(
            app.config["PI_API_URL"].replace("/sprinkle", "/health"),
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "message": "Pi connection successful",
                "pi_response": response.json()
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Pi health check failed: {response.status_code}"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Pi connection failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("🌱 Plant Disease Detection & Sprinkler Control - PC Master Controller")
    print(f"Detection backend: Gemini API")
    print(f"Severity thresholds: Low={app.config['SEVERITY_LOW_THRESHOLD']}%, High={app.config['SEVERITY_HIGH_THRESHOLD']}%")
    print(f"Spray durations: Low={app.config['SPRAY_DURATION_LOW_MS']}ms, High={app.config['SPRAY_DURATION_HIGH_MS']}ms")
    print(f"Pi API URL: {app.config['PI_API_URL']}")
    print("🚀 PC Master Controller ready!")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    ) 