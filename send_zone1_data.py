import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import requests

# Define sensors and GPIO pins
DHT_PIN = board.D17  # DHT11 connected to GPIO 17
MIC_PIN = 27  # KY-037 Digital Output (D0) connected to GPIO 27

# Initialize DHT11 sensor
dht_device = adafruit_dht.DHT11(DHT_PIN)

# Setup GPIO for KY-037
GPIO.setmode(GPIO.BCM)
GPIO.setup(MIC_PIN, GPIO.IN)

# ThingSpeak API details
THINGSPEAK_API_KEY = "L9C5G0C5RD2ZIIT7"  # Replace with your API Key
THINGSPEAK_URL = "https://api.thingspeak.com/update"

def send_to_thingspeak(temperature, humidity, sound_detected):
    """Send sensor data to ThingSpeak."""
    
    if temperature is None or humidity is None:
        print("⚠ Skipping upload: DHT11 returned None values.")
        return

    payload = {
        "api_key": THINGSPEAK_API_KEY,
        "field1": temperature,  # Field 1 = Temperature (Zone 1)
        "field2": humidity,     # Field 2 = Humidity (Zone 1)
        "field3": sound_detected  # Field 3 = Sound Detection (Zone 1)
    }

    try:
        response = requests.get(THINGSPEAK_URL, params=payload)
        if response.status_code == 200:
            print(f"✅ Data sent: Temp={temperature}°C, Humidity={humidity}%, Sound={sound_detected}")
        else:
            print(f"❌ Failed to send data. Response Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")

print("📡 Sending Zone 1 data to ThingSpeak... (Press CTRL+C to stop)")

try:
    while True:
        try:
            # Read temperature and humidity
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            
            # Read KY-037 (Sound Detection)
            sound_detected = 1 if GPIO.input(MIC_PIN) == 0 else 0  # Invert logic (0 = sound detected)

            # Print readings
            print(f"🌡 Temperature: {temperature}°C | 💧 Humidity: {humidity}% | 🎤 Sound: {sound_detected}")

            # Send data to ThingSpeak
            send_to_thingspeak(temperature, humidity, sound_detected)

        except RuntimeError as error:
            print(f"⚠ Sensor error: {error}")

        time.sleep(100)  # ThingSpeak requires a 15-second delay

except KeyboardInterrupt:
    print("\n🛑 Stopping script...")
    GPIO.cleanup()

