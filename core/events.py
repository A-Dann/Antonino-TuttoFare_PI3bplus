from enum import Enum

class Events(str, Enum):
    STATE_CHANGES = "state_changes"
    INPUT_ACTION = "input_action"
    UI_UPDATE = "ui_update"
