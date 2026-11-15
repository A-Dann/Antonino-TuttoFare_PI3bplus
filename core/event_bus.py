import logging
import queue
import threading

log = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers = {}
        self._lock = threading.Lock()

        self._queue = queue.Queue()

    def subscribe(self, event_type: str, callback):
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []

            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)

    def post(self, event_type: str, data=None):
        self._queue.put((event_type, data))

    def dispatch_next_event(self, timeout = 0.1):
        try:
            event_type, data = self._queue.get(timeout=timeout)
        except queue.Empty:
            return False

        self.publish(event_type, data)
        return True

    def publish(self, event_type: str, data=None):
        with self._lock:
            subscribers = list(self._subscribers.get(event_type, []))

        for callback in subscribers:
            try:
                callback(data)
            except Exception:
                log.exception("Error in subscriber for %s", event_type)
