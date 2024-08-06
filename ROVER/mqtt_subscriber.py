
import paho.mqtt.client as mqtt
import hashlib
import json
import logging
from rover import Rover

# Configure logging
logging.basicConfig(level=logging.INFO)

key = "159357"

def msghandler(client, userdata, message):
    try:
        payload_str = message.payload.decode('utf-8')
        payload = json.loads(payload_str)

        rover_data = payload['rover_data']
        received_hash_value = payload['hash_value']
        rover_json_str = json.dumps(rover_data)

        # Compute hash
        hash_object = hashlib.sha256(rover_json_str.encode())
        hash_object.update(key.encode())
        computed_hash_value = hash_object.hexdigest()

        if computed_hash_value == received_hash_value:
            my_rover = Rover.from_json(rover_json_str)
            if my_rover is not None:
                # Log rover data
                logging.info("Button Detected: %s", my_rover.button_detected)
                logging.info("Button Pressed: %s", my_rover.button_pressed)
                logging.info("Flag Detected: %s", my_rover.flag_detected)
                logging.info("Flag Acquired: %s", my_rover.flag_acquired)
                logging.info("Button Color: %s", my_rover.button_color)  # Log button color
                logging.info("Flag Color: %s", my_rover.flag_color)  # Log flag color
                
                # Log timestamp from message
                timestamp = payload.get('timestamp')
                if timestamp:
                    logging.info("Timestamp: %s", timestamp)
            else:
                logging.error("Failed to decode the message into a Rover object")
        else:
            logging.warning("Hash mismatch! Message integrity compromised.")
    except Exception as e:
        logging.error("Error in message handler: %s", e)

mqttc = mqtt.Client()
mqttc.on_message = msghandler

try:
    mqttc.connect("192.168.0.2", 1883, 60)
    mqttc.subscribe("team1/group3", 1)
    mqttc.loop_forever()
except Exception as e:
    logging.error("MQTT connection failed: %s", e)



