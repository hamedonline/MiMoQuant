import customtkinter as ctk
from numpy import uint8
from matplotlib import colormaps
from matplotlib.colors import Normalize
from utils.entities.data_storage import DataStorage
from actions.action_interface import ActionInterface



class ColorMapAction(ActionInterface):
    def __init__(
        self, action_manager, action_priority: int = 0,
        *args, **kwargs
    ) -> None:
        self.values = DataStorage()
        self.values.add(
            priority = ctk.IntVar(value=action_priority),
            is_enabled = ctk.BooleanVar(value=False),
            color_profile = ctk.IntVar(value=0),
        )
        self.manager = action_manager
        self.mappings_dict = {
            0: 'CMRmap',
            1: 'magma',
            2: 'gnuplot2',
            3: 'inferno',
        }


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
            color_profile = self.mappings_dict.get(
                self.values.get('color_profile').get()
            )
            vmin, vmax = img.min(), img.max()
            norm = Normalize(vmin=vmin, vmax=vmax)
            cmap = colormaps.get_cmap(color_profile)
            rgba = cmap(norm(img))
            result_img = (rgba[..., :3] * 255).astype(uint8)
            image_entity.import_from_array(result_img)
            print("Color map action executed.")
            return image_entity
