class EventBus():
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type: str, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data=None):
        if event_type not in self._subscribers:
            return

        for callback in self._subscribers[event_type]:
            try:
                callback(data)
            except Exception as e:
                print(f"Error in subscriber for {event_type}: {e}")

event_bus = EventBus()