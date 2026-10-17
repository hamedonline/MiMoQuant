import customtkinter as ctk
from cv2 import threshold, GaussianBlur, THRESH_OTSU
from utils.entities.data_storage import DataStorage
from actions.action_interface import ActionInterface
from utils.image.general import threshold_image



class GlobalThresholdAction(ActionInterface):
    def __init__(
        self, action_manager, action_priority: int = 0,
        *args, **kwargs
    ) -> None:
        self.values = DataStorage()
        self.values.add(
            priority = ctk.IntVar(value=action_priority),
            is_enabled = ctk.BooleanVar(value=False),
            otsu_enabled = ctk.BooleanVar(value=False),
            global_threshold = ctk.IntVar(value=127),
            # global_threshold_default = 127,
            blurring_enabled = ctk.BooleanVar(value=False),
            blur_kernel_size = ctk.IntVar(value=5),
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
        print("Global Threshold checkbox toggled, current value:", self.is_enabled())
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
            if self.values.get('otsu_enabled').get():
                keep_above, _ = threshold(img, 0, 255, THRESH_OTSU)
                self.values.get('global_threshold').set(int(keep_above))
            else:
                keep_above = self.values.get('global_threshold').get()
            thresholding_conditions = [('<', keep_above, 0), ('>=', keep_above, 255)]

            if self.values.get('blurring_enabled').get():
                blurring_kernel_size = self.values.get('blur_kernel_size').get()
                img = GaussianBlur(img, (blurring_kernel_size, blurring_kernel_size), 0)

            result_img = threshold_image(img, thresholding_conditions)
            image_entity.import_from_array(result_img)
            print("Global Threshold action executed.")
            return image_entity
