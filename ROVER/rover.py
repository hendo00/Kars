
import json

class Rover:
    def __init__(self, found_button, pressed_button, found_flag, captured_flag, ml_mode):
        self.found_button = found_button
        self.pressed_button = pressed_button
        self.found_flag = found_flag
        self.captured_flag = captured_flag
        self.ml_mode = ml_mode

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_str):
        json_dict = json.loads(json_str)
        return Rover(
            json_dict.get('found_button'),
            json_dict.get('pressed_button'),
            json_dict.get('found_flag'),
            json_dict.get('captured_flag'),
        )
