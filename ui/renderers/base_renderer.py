from abc import ABC, abstractmethod

class BaseRenderer(ABC):
    @abstractmethod
    def render(self, content_type: str, data: dict):
        pass