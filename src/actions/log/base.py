import numpy as np
import customtkinter as ctk
from skimage.feature import blob_log
from utils.image.plotting import draw_circle
from utils.entities.data_storage import DataStorage
from actions.action_interface import ActionInterface



class LoGAction(ActionInterface):
    def __init__(
        self, action_manager, action_priority: int = 0,
        *args, **kwargs
    ) -> None:
        self.values = DataStorage()
        self.values.add(
            is_enabled = ctk.BooleanVar(value=False),
            priority = ctk.IntVar(value=action_priority),
            min_sigma = ctk.IntVar(value=1),
            max_sigma = ctk.IntVar(value=50),
            num_sigma = ctk.IntVar(value=10),
            min_threshold = ctk.DoubleVar(value=0.2),
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
        print("LoG checkbox toggled, current value:", self.is_enabled())
        if self.is_enabled():
            # add action to processing queue
            self.manager.add_action(self)
        else:
            # remove action from processing queue
            self.manager.remove_action(self)
        self.manager.inform_action_update()

    def execute(self, image_entity, *args):
        if self.values.get('is_enabled').get():    

            min_sigma = self.values.get('min_sigma').get()
            max_sigma = self.values.get('max_sigma').get()
            num_sigma = self.values.get('num_sigma').get()
            min_threshold = self.values.get('min_threshold').get()

            blobs = blob_log(
                image = image_entity.get_np_image(),
                min_sigma = min_sigma,
                max_sigma = max_sigma,
                num_sigma = num_sigma,
                threshold = min_threshold
            )

            detection_mask = np.zeros(image_entity.get_np_image().shape)
            # create filled circles on detection mask using the detected blobs
            for blob in blobs:
                y, x, r = blob
                detection_mask = draw_circle(detection_mask, x, y, r)

            image_entity.import_from_array(
                detection_mask,
            )

            print("LoG action executed.")
            return image_entity
