import json
import hashlib
import logging
import time
import os
import paho.mqtt.client as mqtt
from rover import Rover
from datetime import datetime, timezone


class RoverMQTTClient:
    def __init__(self, broker_address, broker_port, topic, key, parameters_file='parameters.txt'):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.topic = topic
        self.key = key
        self.parameters_file = parameters_file
        self.last_mod_time = 0
        self.rover = None
        self.mqtt_client = mqtt.Client()

        # Configure logging
        logging.basicConfig(level=logging.INFO)

    def compute_hash(self, rover_data):
        hash_object = hashlib.sha256(rover_data.encode())
        hash_object.update(self.key.encode())
        return hash_object.hexdigest()

    def create_message(self):
        rover_data = self.rover.__dict__  # Serialize Rover data to JSON
        hash_value = self.compute_hash(str(rover_data))
        timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S%z')  # Current timestamp in ISO format
        message = rover_data
        message["hash_value"] = hash_value
        message["timestamp"] = timestamp
        return message

    def parse_json_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            logging.error(f"File {file_path} not found.")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON file: {e}")
            return None
        except Exception as e:
            logging.error(f"Error reading file: {e}")
            return None

    def load_parameters(self):
        params = self.parse_json_file(self.parameters_file)
        if params:
            try:
                self.rover = Rover(**{k: params[k] for k in Rover.__init__.__code__.co_varnames if k in params})
            except TypeError as e:
                logging.error(f"Error creating Rover object: {e}")
                self.rover = None

    def save_parameters(self):
        rover_dict = self.rover.__dict__.copy()
        with open(self.parameters_file, 'w') as file:
            json.dump(rover_dict, file, indent=4)

    def start(self):
        self.mqtt_client.connect(self.broker_address, self.broker_port)
        self.mqtt_client.loop_start()
        self.load_parameters()

        if self.rover is None:
            logging.error("Initial parameters could not be loaded. Exiting...")
            return

        try:
            while True:
                # Check if parameters file has been modified
                try:
                    current_mod_time = os.path.getmtime(self.parameters_file)
                    if current_mod_time != self.last_mod_time:
                        self.last_mod_time = current_mod_time
                        self.load_parameters()
                        if self.rover:
                            logging.info("Loaded new parameters: %s", self.rover.__dict__)
                        else:
                            logging.error("Failed to load new parameters, keeping old parameters.")
                except FileNotFoundError:
                    logging.error("Parameters file not found. Keeping old parameters.")

                # Create and publish the message as JSON
                message = self.create_message()
                msg_info = self.mqtt_client.publish(self.topic, json.dumps(message), qos=1)
                msg_info.wait_for_publish()

                logging.info("Message published with hash value: %s", message['hash_value'])

                # Save the updated Rover parameters to text file
                self.save_parameters()

                # Sleep for a while before sending the next update
                time.sleep(1)  # Adjust sleep duration as needed
        finally:
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()



