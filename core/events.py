from enum import Enum

class Events(str, Enum):
    STATE_CHANGED = "state_changed"
    INPUT_ACTION = "input_action"