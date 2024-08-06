import serial
import json
import time

class SerialComm:
    def __init__(self, port='/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2:1.0-port0', baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

    def send_data(self, data):
        json_data_to_send = json.dumps(data) + '\n'
        self.ser.write(json_data_to_send.encode('utf-8'))

    def receive_data(self):
        if self.ser.in_waiting > 0:
            data = self.ser.readline().decode('utf-8').rstrip()
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                pass
        return None

    def close(self):
        self.ser.close()
