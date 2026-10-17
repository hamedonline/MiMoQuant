import customtkinter as ctk
from gui.widgets.Panel import Panel
from gui.widgets.ValueSlider import ValueSlider
from actions.brightness_gamma.base import BrightnessGammaAction
from managers.Coordinator import Coordinator



class BrightnessGammaWidget(ctk.CTkFrame):
    def __init__(
        self, parent,
        coordinator: Coordinator,
        action_priority: int = 0,
        *args, **kwargs
    ):
        super().__init__(master=parent, *args, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.coordinator = coordinator
        self.action_manager = self.coordinator.ask_for_manager('action')

        # define slider configurations
        self.slider_color = "#3f5051"
        self.slider_padding_config = {'padx':5, 'pady':5, 'ipadx':5, 'ipady':5}

        self.action_object = BrightnessGammaAction(self.action_manager, action_priority=action_priority)

        # define panel
        self.panel_brightness = Panel(parent=self, num_rows=3, num_cols=1)
        self.panel_brightness.grid(
            row=0, column=0,
            pady=4, ipady=8, padx=4, ipadx=8
        )

        # heading label of the panel
        self.heading_label = ctk.CTkLabel(
            master = self.panel_brightness,
            text = "Non-linear Mode: Gamma Correction",
            font = ctk.CTkFont(size=13, weight="bold"),
        )
        self.heading_label.grid(
            row=0, column=0, sticky="ew", 
            padx=12, pady=5,
        )


        # add brightness conditions
        self.enabler = ctk.CTkCheckBox(
            master = self.panel_brightness,
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
            row=1, column=0, sticky="w", 
            padx=12, pady=5,
        )
        self.gamma_slider = ValueSlider(
            parent = self.panel_brightness,
            label = "Inverse Gamma:",
            value_range = (0, 3.0),
            value_object = self.action_object.values.get('gamma'),
            step_precision = 0.05,
            fg_color = self.slider_color,
        )
        self.gamma_slider.grid(row=2, column=0, **self.slider_padding_config)

        ## make action object value traceable (reflect value changes for image manipulation)
        self.action_object.values.get('gamma').trace_add("write", self.action_manager.inform_action_update)
