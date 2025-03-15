import time
import RPi.GPIO as GPIO
import requests  # For sending data to ThingSpeak

# GPIO Pin Configuration
TRIG = 23  # Ultrasonic Sensor TRIG
ECHO = 24  # Ultrasonic Sensor ECHO
RED_LED = 17  # Red Traffic Light
YELLOW_LED = 27  # Yellow Traffic Light
GREEN_LED = 22  # Green Traffic Light

# ThingSpeak API Configuration
THINGSPEAK_API_KEY = "YOUR_API_KEY"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(YELLOW_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)

def measure_distance():
    """Measures distance using the ultrasonic sensor"""
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
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
    """Controls the traffic light"""
    GPIO.output(RED_LED, red)
    GPIO.output(YELLOW_LED, yellow)
    GPIO.output(GREEN_LED, green)

def send_to_thingspeak(distance, status):
    """Sends data to ThingSpeak"""
    payload = {
        'api_key': THINGSPEAK_API_KEY,
        'field1': distance,
        'field2': status
    }
    response = requests.get(THINGSPEAK_URL, params=payload)
    if response.status_code == 200:
        print(f"✅ Data sent to ThingSpeak: Distance={distance} cm, Status={status}")
    else:
        print("⚠️ Error sending data to ThingSpeak")

try:
    while True:
        distance = measure_distance()
        print(f"Measured Distance: {distance} cm")

        if distance <= 30:
            print("🚗 Car Detected! Switching to Green.")
            set_traffic_light(False, False, True)  # Green Light ON
            send_to_thingspeak(distance, "3")  # Green status
            time.sleep(5)

            print("⚠️ Changing to Yellow before Red")
            set_traffic_light(False, True, False)  # Yellow Light ON
            send_to_thingspeak(distance, "2")  # Yellow status
            time.sleep(2)

            print("🔴 Back to Red (Waiting for next car)")
            set_traffic_light(True, False, False)  # Red Light ON
            send_to_thingspeak(distance, "1")  # Red status

        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping script...")
    GPIO.cleanup()

