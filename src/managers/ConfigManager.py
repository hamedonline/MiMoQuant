from managers.Manager import Manager
from managers.Coordinator import Coordinator



class ConfigManager(Manager):
    __slots__ = [
        'coordinator',
        'config_file_path',
        'file_manager',
    ]

    # ************************************************
    def __init__(self, coordinator: Coordinator, config_file_path: str | None = None) -> None:
        super().__init__()
        self.coordinator = coordinator
        self.config_file_path = config_file_path
        # if self.config_file_path is None:
            # create base config and

    def assign_comanagers(self):
        self.file_manager = self.coordinator.ask_for_manager('file')
