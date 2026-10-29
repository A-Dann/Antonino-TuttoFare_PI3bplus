import logging
import threading

log = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers = {}
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, callback):
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []

            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data=None):
        with self._lock:
            subscribers = list(self._subscribers.get(event_type, []))

        for callback in subscribers:
            try:
                callback(data)
            except Exception as e:
                log.error(f"Error in subscriber for {event_type}: {e}")