import time
import RPi.GPIO as GPIO
import requests  # Import library for HTTP requests

# ThingSpeak API Details
THINGSPEAK_API_KEY = "CKVNOWJ4AY1CMLEO"  # Replace with your actual API Key
THINGSPEAK_URL = "https://api.thingspeak.com/update"

# GPIO Pin Configuration
TRIG = 23       # Ultrasonic Trigger Pin
ECHO = 24       # Ultrasonic Echo Pin (⚠️ Use a voltage divider)
RED_LED = 17    # Red LED Pin
YELLOW_LED = 27 # Yellow LED Pin
GREEN_LED = 22  # Green LED Pin

# Distance Thresholds (in centimeters)
CAR_DETECTED_THRESHOLD = 50  # If object is closer than 50cm, consider it a car

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(YELLOW_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)

def measure_distance():
    """Measures distance using the ultrasonic sensor."""
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # Send a short pulse
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # Convert time to distance (cm)
    return round(distance, 2)

def set_traffic_light(red, yellow, green):
    """Sets the traffic light LEDs."""
    GPIO.output(RED_LED, red)
    GPIO.output(YELLOW_LED, yellow)
    GPIO.output(GREEN_LED, green)

def send_to_thingspeak(distance, status_text):
    """Sends traffic light data and distance to ThingSpeak."""
    
    # Convert text status to a number for ThingSpeak
    status_map = {"Red": 1, "Yellow": 2, "Green": 3, "Off": 0}
    status_value = status_map.get(status_text, 0)  # Default to 0 if unknown

    payload = {
        'api_key': THINGSPEAK_API_KEY,
        'field1': distance,
        'field2': status_value  # Send number instead of text
    }

    try:
        response = requests.get(THINGSPEAK_URL, params=payload)
        if response.status_code == 200:
            print(f"✅ Data sent to ThingSpeak: Distance={distance} cm, Status={status_text} ({status_value})")
        else:
            print("⚠️ Error sending data to ThingSpeak")
    except Exception as e:
        print(f"Error: {e}")

# Default State: Red Light ON (No cars detected)
set_traffic_light(True, False, False)
send_to_thingspeak(0, "Red")  # Send default state to ThingSpeak

try:
    while True:
        distance = measure_distance()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - Distance: {distance} cm")

        if distance <= CAR_DETECTED_THRESHOLD:
            print("🚗 Car Detected! Switching to Green.")
            set_traffic_light(False, False, True)  # Green Light ON
            send_to_thingspeak(distance, "Green")  # Send Green (3)
            time.sleep(5)  # Keep green light for 5 seconds

            print("⚠️ Changing to Yellow")
            set_traffic_light(False, True, False)  # Yellow Light ON (directly from Green)
            send_to_thingspeak(distance, "Yellow")  # Send Yellow (2)
            time.sleep(2)  # Yellow for 2 seconds

            print("🔴 Back to Red")
            set_traffic_light(True, False, False)  # Red Light ON (directly from Yellow)
            send_to_thingspeak(distance, "Red")  # Send Red (1)

        time.sleep(1)  # Wait before checking again

except KeyboardInterrupt:
    print("Stopping script...")
    GPIO.cleanup()

