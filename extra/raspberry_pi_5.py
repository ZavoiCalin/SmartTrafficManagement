import serial
import json
import datetime
from azure.iot.device import IoTHubDeviceClient, Message


# Replace with your actual IoT Hub connection string
CONNECTION_STRING = (
    "HostName=SmartTrafficManagement.azure-devices.net;"
    "DeviceId=RaspberryPi5;"
    "SharedAccessKey=h8EcXwnB7NnEeG5kpwXr3xXYT+sEqLp5peC+wcAV0i8="
)

client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

port_name = "/dev/ttyUSB0"
baud_rate = 115200

try:
    ser = serial.Serial(port_name, baud_rate, timeout=1)
    print(f"Connected to Arduino on {port_name}")
except Exception as e:
    print(f"Could not connect to Arduino on {port_name}:", e)
    ser = None

print("Starting data forwarding. Press Ctrl+C to exit.")


try:
    while True:
        if ser and ser.in_waiting > 0:

            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                # Build a JSON payload
                sensor_data = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "arduino_output": line
                }

                # Send to Azure IoT Hub
                message = Message(json.dumps(sensor_data))
                message.content_encoding = "utf-8"
                message.content_type = "application/json"
                client.send_message(message)

                # Print locally (so you can see it via SSH or in logs)
                print(f"Sent to IoT Hub: {sensor_data}")

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    if ser:
        ser.close()
    print("Done.")
