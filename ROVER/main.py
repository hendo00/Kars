import pygame
from serial_comm import SerialComm
import time
from camera import VideoSender
import threading
from mqtt_publish import RoverMQTTClient
import json

rover_port = '/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.1:1.0-port0'
DEBOUNCE_TIME = 0.3  # 300 milliseconds debounce time
DEADZONE = 0.1  # Adjusted value
vel = 5  # Adjusted velocity

def map_value(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def toggle_key(parameters, key):
    if key in parameters:
        parameters[key] = not parameters[key]

def update_parameters(action):
    parameters_file = 'parameters.txt'
    try:
        with open(parameters_file, 'r') as file:
            parameters = json.load(file)
    except FileNotFoundError:
        print(f"File {parameters_file} not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Toggle the parameters based on the action
    if action == 'A':
        toggle_key(parameters, 'found_button')
    elif action == 'B':
        toggle_key(parameters, 'pressed_button')
    elif action == 'X':
        toggle_key(parameters, 'found_flag')
    elif action == 'Y':
        toggle_key(parameters, 'captured_flag')
    elif action == 'L1':
        toggle_key(parameters, 'ml_mode')

    try:
        with open(parameters_file, 'w') as file:
            json.dump(parameters, file, indent=4)
        print(f"Updated parameters: {parameters}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def get_axis_with_deadzone(axis_value, deadzone):
    """Apply a dead zone to joystick axis values."""
    if abs(axis_value) < deadzone:
        return 0
    return axis_value

def rover():
    rover_serial = SerialComm(port=rover_port, baudrate=115200, timeout=1)
    pygame.init()
    clock = pygame.time.Clock()

    joystick = None
    last_button_press_time = {'A': 0, 'B': 0, 'X': 0, 'Y': 0, 'L1': 0}

    def is_debounce(action):
        current_time = time.time()
        if current_time - last_button_press_time[action] > DEBOUNCE_TIME:
            last_button_press_time[action] = current_time
            return False
        return True

    try:
        while True:
            if joystick is None or not pygame.joystick.get_count():
                print("Waiting for joystick connection...")
                coords = {"yL": 0, "xR": 0}
                rover_serial.send_data(coords)
                while pygame.joystick.get_count() == 0:
                    time.sleep(1)
                    pygame.joystick.quit()
                    pygame.joystick.init()

                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                print("Joystick initialized")

            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    print(pygame.key.name(event.key))

            if joystick:
                # Get and apply dead zone to axis values
                y_axis_value = get_axis_with_deadzone(joystick.get_axis(3), DEADZONE)
                x_axis_value = get_axis_with_deadzone(joystick.get_axis(0), DEADZONE)

                # Calculate the joystick values
                y = round(-y_axis_value * vel)
                x = round(x_axis_value * vel)

                # Map axis values
                y = map_value(y, -vel, vel, 255, -255)
                x = map_value(x, -vel, vel, -255, 255)

                # Debugging output
                print(f"Raw Y: {y_axis_value}, Mapped Y: {y}")
                print(f"Raw X: {x_axis_value}, Mapped X: {x}")

                # Button handling
                if joystick.get_button(0):  # 'A'
                    if not is_debounce('A'):
                        print('A')
                        update_parameters('A')
                elif joystick.get_button(1):  # 'B'
                    if not is_debounce('B'):
                        print('B')
                        update_parameters('B')
                elif joystick.get_button(3):  # 'X'
                    if not is_debounce('X'):
                        print('X')
                        update_parameters('X')
                elif joystick.get_button(4):  # 'Y'
                    if not is_debounce('Y'):
                        print('Y')
                        update_parameters('Y')
                elif joystick.get_button(6):  # 'L1'
                    if not is_debounce('L1'):
                        print('L1')
                        update_parameters('L1')

                # Send data to rover
                coords = {"yL": y, "xR": x}
                rover_serial.send_data(coords)
                received_data = rover_serial.receive_data()
                if received_data:
                    print(f'Received from ESP32: {received_data}')



    except KeyboardInterrupt:
        rover_serial.close()
        print("Serial communication stopped.")
    finally:
        pygame.quit()
        exit()

def stream(station_number):
    sender = VideoSender(3, station_number)
    sender.send_video()

def publish():
    client = RoverMQTTClient(broker_address="192.168.0.2", broker_port=1883, topic="team2/group3", key="b3Nk5T")
    client.start()

if __name__ == "__main__":
    # Threads
    rover_ctrl = threading.Thread(target=rover)
    camera = threading.Thread(target=stream, args=(4,))
    # publisher = threading.Thread(target=publish)

    # Starting threads
    camera.start()
    rover_ctrl.start()
    # publisher.start()

    # Joining threads
    camera.join()
    rover_ctrl.join()
    # publisher.join()
