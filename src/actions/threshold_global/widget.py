import customtkinter as ctk
from gui.widgets.Panel import Panel
from gui.widgets.ValueSlider import ValueSlider
from actions.threshold_global.base import GlobalThresholdAction
from managers.Coordinator import Coordinator



class GlobalThresholdWidget(ctk.CTkFrame):
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

        self.action_object = GlobalThresholdAction(self.action_manager, action_priority=action_priority)

        # define panels
        self.panel_threshold = Panel(parent=self, num_rows=3, num_cols=1)
        self.panel_threshold.grid(
            row=0, column=0,
            pady=4, ipady=8, padx=4, ipadx=8
        )
        self.panel_blurring = Panel(parent=self, num_rows=2, num_cols=1)
        self.panel_blurring.grid(
            row=1, column=0,
            pady=4, ipady=8, padx=4, ipadx=8
        )

        # # add thresholding conditions
        self.enabler = ctk.CTkCheckBox(
            master=self.panel_threshold,
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
        self.otsu_enabler = ctk.CTkCheckBox(
            master = self.panel_threshold,
            text = "Otsu?",
            command = self.action_object.toggle,
            variable = self.action_object.values.get('otsu_enabled'),
            onvalue = True,
            offvalue = False,
            fg_color = self.slider_color,
            hover_color = "#15ba85",
            checkmark_color = "#20e9a8",
        )
        self.otsu_enabler.grid(
            row=1, column=0, sticky="w", 
            padx=12, pady=5,
        )
        self.threshold_slider = ValueSlider(
            parent=self.panel_threshold,
            label="Global Threshold:",
            value_range=(0, 255),
            value_object=self.action_object.values.get('global_threshold'),
            step_precision=1,
            fg_color=self.slider_color,
        )
        self.threshold_slider.grid(row=2, column=0, **self.slider_padding_config)

        # add blurring conditions
        self.blurring_enabler = ctk.CTkCheckBox(
            master = self.panel_blurring,
            text = "Blurring?",
            command = self.action_object.toggle,
            variable = self.action_object.values.get('blurring_enabled'),
            onvalue = True,
            offvalue = False,
            fg_color = self.slider_color,
            hover_color = "#15ba85",
            checkmark_color = "#20e9a8",
        )
        self.blurring_enabler.grid(
            row=0, column=0, sticky="w", 
            padx=12, pady=5,
        )
        self.blurring_kernel_size_slider = ValueSlider(
            parent = self.panel_blurring,
            label = "Blurring Size:",
            value_range = (1, 55),
            value_object = self.action_object.values.get('blur_kernel_size'),
            step_precision = 2,
            fg_color = self.slider_color,
        )
        self.blurring_kernel_size_slider.grid(row=1, column=0, **self.slider_padding_config)      


        ## make action object value traceable (reflect value changes for image manipulation)
        self.action_object.values.get('otsu_enabled').trace_add("write", self.threshold_slider.update_via_tracing)
        self.action_object.values.get('global_threshold').trace_add("write", self.action_manager.inform_action_update)
        self.action_object.values.get('global_threshold').trace_add("write", self.threshold_slider.update_via_tracing)
        self.action_object.values.get('blur_kernel_size').trace_add("write", self.action_manager.inform_action_update)
