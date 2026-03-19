import time
import board
import adafruit_dht

dht = adafruit_dht.DHT11(board.D4)  # GPIO 4

while True:
    try:
        temp = dht.temperature
        humidity = dht.humidity
        print(f"Temp: {temp}°C, Humidity: {humidity}%")
    except Exception as e:
        print("Read failed:", e)
    time.sleep(2)
