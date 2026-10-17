import customtkinter as ctk
from gui.widgets.Panel import Panel
from actions.color_map.base import ColorMapAction
from managers.Coordinator import Coordinator



class ColorMapWidget(ctk.CTkFrame):
    def __init__(
        self, parent,
        coordinator: Coordinator,
        action_priority: int = 0,
        *args, **kwargs
    ):
        super().__init__(master=parent, *args, **kwargs)
        self.rowconfigure((0, 1), weight=1)
        self.columnconfigure(0, weight=1)

        self.coordinator = coordinator
        self.action_manager = self.coordinator.ask_for_manager('action')

        # define slider configurations
        self.slider_color = "#3f5051"
        self.slider_padding_config = {'padx':5, 'pady':5, 'ipadx':5, 'ipady':5}

        self.action_object = ColorMapAction(self.action_manager, action_priority=action_priority)


        # define panel
        self.panel_colormap = Panel(parent=self, num_rows=2, num_cols=2)
        self.panel_colormap.grid(
            row=0, column=0,
            pady=4, ipady=8, padx=4, ipadx=8
        )

        # add color map conditions
        self.enabler = ctk.CTkCheckBox(
            master = self.panel_colormap,
            text = "Enabled",
            command = self.action_object.toggle,
            variable = self.action_object.values.get('is_enabled'),
            onvalue = True,
            offvalue = False,
            fg_color = self.slider_color,
            hover_color = "#15ba85",
            checkmark_color = "#20e9a8",
        )
        self.enabler.grid(
            row=0, column=0, columnspan=2, sticky="w",
            padx=12, pady=5,
        )
        
        self.color_profile_label = ctk.CTkLabel(
            master = self.panel_colormap,
            text = "Color Profile:"
        )
        self.color_profile_label.grid(
            row=1, column=0, sticky="w",
            padx=12, pady=5,
        )
        self.color_profile_option = ctk.StringVar(value="CMR")
        self.color_profile = ctk.CTkOptionMenu(
            master = self.panel_colormap,
            values = ["CMR", "Magma", "GNU", "Inferno"],
            variable = self.color_profile_option,
            command = self.set_color_profile,
            fg_color = self.slider_color,
            button_color = "#0F805A",
            button_hover_color = "#15ba85",
        )
        self.color_profile.grid(
            row=1, column=1, sticky="e",
            padx=12, pady=5,
        )

        # make action object value traceable (reflect value changes for image manipulation)
        self.action_object.values.get('color_profile').trace_add("write", self.action_manager.inform_action_update)


    def set_color_profile(self, choice: str):
        color_options_dict = {
            "CMR": 0,
            "Magma": 1,
            "GNU": 2,
            "Inferno": 3,
        }
        self.action_object.values.get('color_profile').set(color_options_dict.get(choice, 0))
