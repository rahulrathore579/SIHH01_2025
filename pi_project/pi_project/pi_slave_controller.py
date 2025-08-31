#!/usr/bin/env python3
"""
Raspberry Pi Slave Controller - Sprinkler Actuator Only
Listens for commands from PC and controls GPIO for sprinkler
"""

from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pi_slave.log'),
        logging.StreamHandler()
    ]
)

# Create Flask app
app = Flask(__name__)

# GPIO Configuration
GPIO_PIN_SPRINKLER = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN_SPRINKLER, GPIO.OUT)
GPIO.output(GPIO_PIN_SPRINKLER, GPIO.LOW)

# Statistics
total_commands = 0
total_sprays = 0
total_duration = 0

@app.route('/sprinkle', methods=['POST'])
def sprinkle():
    """Main endpoint to receive sprinkler commands from PC"""
    global total_commands, total_sprays, total_duration
    
    try:
        # Get JSON payload from PC
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        action = data.get('action', 'off')
        duration = data.get('duration', 0)
        
        logging.info(f"📡 Received command: action={action}, duration={duration}ms")
        total_commands += 1
        
        # Control sprinkler based on action
        if action == "on" and duration > 0:
            # Activate sprinkler
            logging.info(f"💧 Activating sprinkler for {duration}ms")
            
            GPIO.output(GPIO_PIN_SPRINKLER, GPIO.HIGH)
            time.sleep(duration / 1000.0)  # Convert ms to seconds
            GPIO.output(GPIO_PIN_SPRINKLER, GPIO.LOW)
            
            total_sprays += 1
            total_duration += duration
            
            logging.info(f"✅ Sprinkler activated for {duration}ms")
            
            return jsonify({
                "status": "sprinkled",
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "message": f"Sprinkler activated for {duration}ms"
            })
            
        elif action == "off":
            # Ensure sprinkler is off
            GPIO.output(GPIO_PIN_SPRINKLER, GPIO.LOW)
            
            logging.info("🌱 Sprinkler kept off - Plant is healthy")
            
            return jsonify({
                "status": "off",
                "duration": 0,
                "timestamp": datetime.now().isoformat(),
                "message": "Sprinkler kept off - Plant is healthy"
            })
            
        else:
            return jsonify({
                "status": "error",
                "message": f"Invalid action: {action} or duration: {duration}"
            }), 400
            
    except Exception as e:
        logging.error(f"❌ Error in sprinkle endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Internal error: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gpio_pin": GPIO_PIN_SPRINKLER,
        "sprinkler_state": "HIGH" if GPIO.input(GPIO_PIN_SPRINKLER) else "LOW",
        "statistics": {
            "total_commands": total_commands,
            "total_sprays": total_sprays,
            "total_duration_ms": total_duration
        }
    })

@app.route('/status', methods=['GET'])
def status():
    """Get current status"""
    return jsonify({
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "gpio_pin": GPIO_PIN_SPRINKLER,
        "sprinkler_state": "HIGH" if GPIO.input(GPIO_PIN_SPRINKLER) else "LOW",
        "uptime": time.time() - getattr(app, 'start_time', time.time())
    })

@app.route('/test', methods=['POST'])
def test_sprinkler():
    """Test endpoint to manually test sprinkler"""
    try:
        data = request.get_json() or {}
        test_duration = data.get('duration', 1000)  # Default 1 second
        
        logging.info(f"🧪 Testing sprinkler for {test_duration}ms")
        
        # Test activation
        GPIO.output(GPIO_PIN_SPRINKLER, GPIO.HIGH)
        time.sleep(test_duration / 1000.0)
        GPIO.output(GPIO_PIN_SPRINKLER, GPIO.LOW)
        
        return jsonify({
            "status": "success",
            "message": f"Test completed - sprinkler activated for {test_duration}ms",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"❌ Test error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Test failed: {str(e)}"
        }), 500

@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    """Emergency stop - turn off sprinkler immediately"""
    try:
        GPIO.output(GPIO_PIN_SPRINKLER, GPIO.LOW)
        logging.warning("🚨 EMERGENCY STOP - Sprinkler turned off")
        
        return jsonify({
            "status": "emergency_stop",
            "message": "Sprinkler turned off immediately",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"❌ Emergency stop error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Emergency stop failed: {str(e)}"
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    return jsonify({
        "statistics": {
            "total_commands": total_commands,
            "total_sprays": total_sprays,
            "total_duration_ms": total_duration,
            "average_duration": total_duration / total_sprays if total_sprays > 0 else 0
        },
        "timestamp": datetime.now().isoformat()
    })

def cleanup():
    """Cleanup GPIO on shutdown"""
    try:
        GPIO.output(GPIO_PIN_SPRINKLER, GPIO.LOW)
        GPIO.cleanup()
        logging.info("✅ GPIO cleanup completed")
    except Exception as e:
        logging.error(f"❌ GPIO cleanup error: {e}")

if __name__ == '__main__':
    app.start_time = time.time()
    
    logging.info("🌱 Raspberry Pi Slave Controller Starting...")
    logging.info(f"💧 Sprinkler GPIO Pin: {GPIO_PIN_SPRINKLER}")
    logging.info("📡 Listening for commands from PC Master Controller")
    logging.info("🚀 Pi Slave Controller ready!")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        logging.info("🛑 Shutting down Pi Slave Controller...")
    finally:
        cleanup()
