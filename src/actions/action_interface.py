from abc import ABC, abstractmethod


class ActionInterface(ABC):
    @abstractmethod
    def execute(self):
        pass