import customtkinter as ctk
from gui.widgets.Panel import Panel
from gui.widgets.ValueSlider import ValueSlider
from actions.mexhat.base import MexHatAction
from managers.Coordinator import Coordinator



class MexHatWidget(ctk.CTkFrame):
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
        self.state_manager = self.coordinator.ask_for_manager('state')
        self.display_manager = self.coordinator.ask_for_manager('display')

        # define slider configurations
        self.slider_color = "#3f5051"
        self.slider_padding_config = {'padx':5, 'pady':5, 'ipadx':5, 'ipady':5}

        self.action_object = MexHatAction(
            action_manager=self.action_manager, action_priority=action_priority,
            state_manager=self.state_manager, display_manager=self.display_manager
        )

        self.panel = Panel(parent=self, num_rows=4, num_cols=1)
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
        self.width_slider = ValueSlider(
            parent=self.panel,
            label="Hat Width:",
            value_range=(1, 20),
            value_object=self.action_object.values.get('width'),
            step_precision=0.5,
            fg_color=self.slider_color,
        )
        self.width_slider.grid(row=1, column=0, **self.slider_padding_config)

        self.kernel_size_slider = ValueSlider(
            parent=self.panel,
            label="Kernel Size:",
            value_range=(3, 99),
            value_object=self.action_object.values.get('kernel_size'),
            step_precision=2,
            fg_color=self.slider_color,
        )
        self.kernel_size_slider.grid(row=2, column=0, **self.slider_padding_config)

        self.negative_amplify_slider = ValueSlider(
            parent=self.panel,
            label="Negative Amplification:",
            value_range=(0, 10),
            value_object=self.action_object.values.get('negative_amplification'),
            step_precision=0.01,
            fg_color=self.slider_color,
        )
        self.negative_amplify_slider.grid(row=3, column=0, **self.slider_padding_config)

        # make action object values traceable (reflect value changes for image manipulation)
        # self.action_object.values.get('is_enabled').trace_add("write", self.action_object.execute)
        self.action_object.values.get('width').trace_add("write", self.action_manager.inform_action_update)
        self.action_object.values.get('kernel_size').trace_add("write", self.action_manager.inform_action_update)
        self.action_object.values.get('negative_amplification').trace_add("write", self.action_manager.inform_action_update)
