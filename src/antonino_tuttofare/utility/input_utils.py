import sys
import select
from antonino_tuttofare import state

class StateChangedInterrupt(Exception):
    """Custom exception raised when a background voice command changes the state,
    immediately interrupting any blocking input prompt across the application.
    """
    pass


def universal_input(prompt: str = "") -> str:
    """Reads from stdin using a non-blocking select loop, raising an interrupt
    if the application state changes in the background via voice commands.
    """
    if prompt:
        sys.stdout.write(prompt)
        sys.stdout.flush()

    while True:
        # Check if the AI agent changed the state in the background
        if state.state_changed_event.is_set():
            raise StateChangedInterrupt()

        # Non-blocking check on stdin with a short timeout
        try:
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                line = sys.stdin.readline()
                if not line:
                    return ""
                return line.strip()
        except (IOError, OSError):
            pass