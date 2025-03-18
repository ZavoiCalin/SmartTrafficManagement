import time
import json
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from pms5003 import PMS5003, ReadTimeoutError
from azure.iot.device import IoTHubDeviceClient, Message

# Azure IoT Hub connection string
CONNECTION_STRING = "Your_Azure_IoT_Hub_Connection_String"

# Hardware SPI configuration for MCP3008 (for MQ-7 and MiCS-5524)
SPI_PORT = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# PMS5003 sensor initialization
pms5003 = PMS5003()

# Create an IoT Hub client
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

def read_co_sensor():
    co_value = mcp.read_adc(0)  # Assuming MQ-7 is connected to channel 0
    return co_value

def read_no2_sensor():
    no2_value = mcp.read_adc(1)  # Assuming MiCS-5524 is connected to channel 1
    return no2_value

def read_pm25_sensor():
    try:
        data = pms5003.read()
        pm25_value = data.pm_ug_per_m3(2.5)
        return pm25_value
    except ReadTimeoutError:
        return None

def read_sensor_data():
    co_value = read_co_sensor()
    no2_value = read_no2_sensor()
    pm25_value = read_pm25_sensor()

    if pm25_value is not None:
        return {
            "sensorType": "AirQualitySensors",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "data": {
                "co": co_value,
                "no2": no2_value,
                "pm25": pm25_value
            }
        }
    else:
        return None

def send_telemetry_to_iothub(telemetry_data):
    message = Message(json.dumps(telemetry_data))
    message.content_encoding = "utf-8"
    message.content_type = "application/json"
    client.send_message(message)
    print(f"Sent data to IoT Hub: {json.dumps(telemetry_data)}")

def main():
    while True:
        telemetry_data = read_sensor_data()
        if telemetry_data:
            send_telemetry_to_iothub(telemetry_data)
        time.sleep(30)  # Adjust the frequency as needed

if __name__ == "__main__":
    main()
