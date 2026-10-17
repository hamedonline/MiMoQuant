import numpy as np
import customtkinter as ctk
from astropy.convolution import RickerWavelet2DKernel
from utils.image.convolution import convolve2D_opencv
from utils.image.kernel import normalize_kernel, amplify_negative_values
from utils.entities.data_storage import DataStorage
from actions.action_interface import ActionInterface



class MexHatAction(ActionInterface):
    def __init__(
        self, 
        state_manager,
        display_manager,
        action_manager, action_priority: int = 0,
        *args, **kwargs
    ) -> None:
        self.values = DataStorage()
        self.values.add(
            is_enabled = ctk.BooleanVar(value=False),
            priority = ctk.IntVar(value=action_priority),
            width = ctk.DoubleVar(value=2.0),
            kernel_size = ctk.IntVar(value=7),
            negative_amplification = ctk.DoubleVar(value=0.0),
        )
        self.manager = action_manager
        self.state_manager = state_manager
        self.display_manager = display_manager

    def get_priority(self):
        return self.values.get('priority').get()

    def is_enabled(self):
        return self.values.get('is_enabled').get()

    def enable(self):
        self.values.get('is_enabled').set(True)

    def disable(self):
        self.values.get('is_enabled').set(False)

    def toggle(self):
        print("MexHat checkbox toggled, current value:", self.is_enabled())
        if self.is_enabled():
            # add action to processing queue
            self.manager.add_action(self)
        else:
            # remove action from processing queue
            self.manager.remove_action(self)
        self.manager.inform_action_update()

    def execute(self, image_entity, *args):
        if self.values.get('is_enabled').get():

            ricker_2d_kernel = RickerWavelet2DKernel(
                width = self.values.get('width').get(),
                x_size = self.values.get('kernel_size').get(),
                y_size = self.values.get('kernel_size').get()
            )

            normalized_kernel = normalize_kernel(ricker_2d_kernel.array)

            neg_amplification_factor = self.values.get('negative_amplification').get()
            if neg_amplification_factor > 0:
                mexican_hat_kernel = normalize_kernel(
                    amplify_negative_values(
                        normalized_kernel,
                        neg_amplification_factor
                    )
                )
            else:
                mexican_hat_kernel = normalize_kernel(ricker_2d_kernel.array)

            # padding the image to avoid magnitude loss and edge effects
            pad_size = int(self.values.get('kernel_size').get() // 2)
            if self.state_manager.is_roi_from_source():
                # reselect the image array from the source image, this time with padding added to it
                roi_start_coord, roi_end_coord = self.display_manager.get_roi_coords()
                roi_start_coord_padded, roi_end_coord_padded = (
                    roi_start_coord[0] - pad_size,
                    roi_start_coord[1] - pad_size
                ), (
                    roi_end_coord[0] + pad_size,
                    roi_end_coord[1] + pad_size
                )
                img_to_process = self.display_manager.get_source_image().get_np_image()[
                    roi_start_coord_padded[1]:roi_end_coord_padded[1],
                    roi_start_coord_padded[0]:roi_end_coord_padded[0]
                ]
            else:
                # img_to_process = np.pad(
                #     array = image_entity.get_np_image(),
                #     pad_width = (pad_size, pad_size),
                #     mode='constant',
                #     constant_values=0
                # )
                img_to_process = np.zeros(
                    (image_entity.get_np_image().shape[0] + 2 * pad_size, image_entity.get_np_image().shape[1] + 2 * pad_size)
                )
                img_to_process[pad_size:-pad_size, pad_size:-pad_size] = image_entity.get_np_image()

            result_img = convolve2D_opencv(
                image = img_to_process,
                kernel = mexican_hat_kernel,
                # padding = pad_size,
                filter_type="conv",
                border_type = 1
            )
            # only keep the original image size after convolution (remove previously added padding)
            final_image = result_img[
                pad_size:result_img.shape[0] - pad_size,
                pad_size:result_img.shape[1] - pad_size
                # result_img[
                #     pad_size:-pad_size, pad_size:-pad_size
                # ]
            ]
            image_entity.import_from_array(
                final_image,
            )
            # print(img_to_process.shape, result_img.shape, final_image.shape)

            print("MexHat action executed.")
            return image_entity
