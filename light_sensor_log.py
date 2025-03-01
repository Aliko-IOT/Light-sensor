import time
import requests
import RPi.GPIO as GPIO

# Setup GPIO
SENSOR_PIN = 17  # GPIO pin connected to the sensor's DO (digital output)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

# ThingSpeak settings
THINGSPEAK_API_KEY = "MNBVMEN1BQ1F90HQ"  # Replace with your actual ThingSpeak Write API Key
THINGSPEAK_URL = "https://api.thingspeak.com/update"

# File to store sensor data
LOG_FILE = "light_sensor_data.csv"

# Write header to file (only once)
with open(LOG_FILE, "a") as file:
    file.write("Timestamp,Light_Status\n")

def send_to_thingspeak(light_status):
    """Send sensor data to ThingSpeak"""
    payload = {
        'api_key': THINGSPEAK_API_KEY,
        'field1': light_status
    }
    try:
        response = requests.get(THINGSPEAK_URL, params=payload)
        if response.status_code == 200:
            print(f"Data sent to ThingSpeak: {light_status}")
        else:
            print("Error sending data to ThingSpeak")
    except Exception as e:
        print(f"Error: {e}")

# Main loop to monitor light changes and log to file
try:
    while True:
        # Get current timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Read sensor value
        if GPIO.input(SENSOR_PIN) == GPIO.LOW:  # Light detected
            light_status = 1  # Bright light
            print(f"{timestamp} - Bright Light Detected! (Light ON)")
        else:
            light_status = 0  # Low light
            print(f"{timestamp} - Low Light Detected! (Light OFF)")

        # Write to file
        with open(LOG_FILE, "a") as file:
            file.write(f"{timestamp},{light_status}\n")

        # Send data to ThingSpeak
        send_to_thingspeak(light_status)

        # Wait for 5 seconds before the next reading
        time.sleep(5)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()

