import customtkinter as ctk
from cv2 import convertScaleAbs
from utils.entities.data_storage import DataStorage
from actions.action_interface import ActionInterface



class BrightnessLinearAction(ActionInterface):
    def __init__(
        self, action_manager, action_priority: int = 0,
        *args, **kwargs
    ) -> None:
        self.values = DataStorage()
        self.values.add(
            priority = ctk.IntVar(value=action_priority),
            is_enabled = ctk.BooleanVar(value=False),
            alpha = ctk.DoubleVar(value=1.2),
            beta = ctk.IntVar(value=40)
        )
        self.manager = action_manager

    def get_priority(self):
        return self.values.get('priority').get()

    def is_enabled(self):
        return self.values.get('is_enabled').get()

    def enable(self):
        self.values.get('is_enabled').set(True)

    def disable(self):
        self.values.get('is_enabled').set(False)

    def toggle(self):
        if self.is_enabled():
            # add action to processing queue
            self.manager.add_action(self)
        else:
            # remove action from processing queue
            self.manager.remove_action(self)
        self.manager.inform_action_update()

    def execute(self, image_entity, *args):
        if self.values.get('is_enabled').get():
            img = image_entity.get_np_image()
            alpha = self.values.get('alpha').get()
            beta = self.values.get('beta').get()
            result_img = convertScaleAbs(img, alpha=alpha, beta=beta)
            image_entity.import_from_array(result_img)
            print("Brightness action executed.")
            return image_entity
