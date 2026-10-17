import customtkinter as ctk
from gui.widgets.Panel import Panel
from gui.widgets.ValueSlider import ValueSlider
from actions.doh.base import DoHAction
from managers.Coordinator import Coordinator



class DoHWidget(ctk.CTkFrame):
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

        self.action_object = DoHAction(action_manager=self.action_manager, action_priority=action_priority)

        self.panel = Panel(parent=self, num_rows=5, num_cols=1)
        self.panel.grid(
            row=0, column=0,
            pady=4, ipady=8, padx=4, ipadx=8
        )

        # add enabler checkbox
        self.enabler = ctk.CTkCheckBox(
            master = self.panel,
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
            row=0, column=0, sticky="w", 
            padx=12, pady=5,
        )

        # add sliders
        self.min_sigma_slider = ValueSlider(
            parent=self.panel,
            label="Min Sigma:",
            value_range=(1, 20),
            value_object=self.action_object.values.get('min_sigma'),
            step_precision=1,
            fg_color=self.slider_color,
        )
        self.min_sigma_slider.grid(row=1, column=0, **self.slider_padding_config)

        self.max_sigma_slider = ValueSlider(
            parent=self.panel,
            label="Max Sigma:",
            value_range=(10, 50),
            value_object=self.action_object.values.get('max_sigma'),
            step_precision=1,
            fg_color=self.slider_color,
        )
        self.max_sigma_slider.grid(row=2, column=0, **self.slider_padding_config)

        # number of intermediate values of standard deviations to consider between min_sigma and max_sigma
        self.num_sigma_slider = ValueSlider(
            parent=self.panel,
            label="Number of Sigma:",
            value_range=(1, 20),
            value_object=self.action_object.values.get('num_sigma'),
            step_precision=1,
            fg_color=self.slider_color,
        )
        self.num_sigma_slider.grid(row=3, column=0, **self.slider_padding_config)

        self.threshold_slider = ValueSlider(
            parent=self.panel,
            label="Scale Threshold:",
            value_range=(0.01, 1),
            value_object=self.action_object.values.get('min_threshold'),
            step_precision=0.01,
            fg_color=self.slider_color,
        )
        self.threshold_slider.grid(row=4, column=0, **self.slider_padding_config)


        # make action object values traceable (reflect value changes for image manipulation)
        self.action_object.values.get('min_sigma').trace_add("write", self.action_manager.inform_action_update)
        self.action_object.values.get('max_sigma').trace_add("write", self.action_manager.inform_action_update)
        self.action_object.values.get('num_sigma').trace_add("write", self.action_manager.inform_action_update)
        self.action_object.values.get('min_threshold').trace_add("write", self.action_manager.inform_action_update)
