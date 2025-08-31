import RPi.GPIO as GPIO
import time
import requests

# GPIO setup
RELAY_PIN = 17  # GPIO17

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay off (assuming active LOW)

# API endpoint (replace with your actual API URL)
API_URL = "https://api.plant.id/v3/health_assessment"

def get_plant_health():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        # Assuming API returns JSON like {"health": "Healthy"} or {"health": "Infected"}
        return data.get("health", "Unknown")
    except Exception as e:
        print(f"Error calling API: {e}")
        return "Unknown"

def activate_pump(duration=10):
    print("Activating pump...")
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn relay ON (active LOW)
    time.sleep(duration)
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn relay OFF
    print("Pump deactivated.")

def main():
    while True:
        health_status = get_plant_health()
        print(f"Plant health status: {health_status}")
        if health_status == "Infected":
            activate_pump(duration=10)  # Pump on for 10 seconds
        else:
            print("Plant is healthy. Pump remains off.")
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program stopped by user.")
    finally:
        GPIO.cleanup()
