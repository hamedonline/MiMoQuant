import customtkinter as ctk
from cv2 import threshold, GaussianBlur, THRESH_OTSU
from utils.entities.data_storage import DataStorage
from actions.action_interface import ActionInterface
from utils.image.general import threshold_image, threshold_image_adaptive



class AdaptiveThresholdAction(ActionInterface):
    def __init__(
        self, action_manager, action_priority: int = 0,
        *args, **kwargs
    ) -> None:
        self.values = DataStorage()
        self.values.add(
            priority = ctk.IntVar(value=action_priority),
            is_enabled = ctk.BooleanVar(value=False),
            blurring_enabled = ctk.BooleanVar(value=True),
            blur_kernel_size = ctk.IntVar(value=5),
            adaptive_method = ctk.IntVar(value=0),
            block_size = ctk.IntVar(value=3),
            noiseReduction_enabled = ctk.BooleanVar(value=True),
            noiseReduction_factor = ctk.DoubleVar(value=0.3)
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
            if self.values.get('noiseReduction_enabled').get():
                otsu_value = threshold(img, 0, 255, THRESH_OTSU)[0]
                lowest_intensity = int(otsu_value * self.values.get('noiseReduction_factor').get())
                thresholding_conditions = [('<', lowest_intensity, lowest_intensity)]
                img = threshold_image(img, thresholding_conditions)
            if self.values.get('blurring_enabled').get():
                blurring_kernel_size = self.values.get('blur_kernel_size').get()
                img = GaussianBlur(img, (blurring_kernel_size, blurring_kernel_size), 0)
            result_img = threshold_image_adaptive(
                image = img,
                adaptive_method = self.values.get('adaptive_method').get(),
                block_size = self.values.get('block_size').get(),
            )
            image_entity.import_from_array(result_img)
            print("Adaptive Threshold action executed.")
            return image_entity
