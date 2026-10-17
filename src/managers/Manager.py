from utils.entities.data_storage import DataStorage
from utils.entities.data_types import ExecutionFunction
from utils.entities.execution_queue import ExecutionQueue



class Manager:
    __slots__ = [
        'storage',
        'execution_queue',
    ]

    def __init__(self):
        self.storage: DataStorage = DataStorage()
        self.execution_queue: ExecutionQueue = ExecutionQueue()

    def assign_comanagers(self):
        pass

    def perform_post_init_tasks(self):
        pass

    def store(self, data_dict: dict = {}, **kwargs):
        self.storage.add(data_dict, **kwargs)

    def retrieve(self, key):
        return self.storage.retrieve(key)

    def remove(self, key):
        self.storage.remove(key)

    def has_key(self, key):
        return self.storage.key_exists(key)

    def add_to_execution_queue(self, *functions: ExecutionFunction) -> None:
        self.execution_queue.add_functions(*functions)

    def execute_and_then_clear_queue(self) -> None:
        self.execution_queue.execute_all()
        self.execution_queue.clear()
