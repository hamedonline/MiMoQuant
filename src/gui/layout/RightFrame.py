# import tkinter as tk
from tkinter import ttk
from managers.Coordinator import Coordinator
from gui.widgets.TabsFrame import TabsFrame
# from actions.log.widget import LoGWidget
# from actions.dog.widget import DoGWidget
# from actions.doh.widget import DoHWidget
# from actions.mexhat.widget import MexHatWidget
from actions.brightness_gamma.widget import BrightnessGammaWidget
from actions.brightness_linear.widget import BrightnessLinearWidget
from actions.color_map.widget import ColorMapWidget
from actions.threshold_global.widget import GlobalThresholdWidget
from actions.threshold_adaptive.widget import AdaptiveThresholdWidget



class RightFrame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, coordinator: Coordinator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.coordinator = coordinator

        self.style = ttk.Style(self)
        self.style.configure(
            "right_frame.TFrame",
            # background="cyan"
        )
        self.configure(style="right_frame.TFrame")

        # define grid for the right frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1), weight=1)

        self.create_widgets()


    def create_widgets(self):
        # filter options tab
        self.filter_options_tab = TabsFrame(
            parent = self,
            tab_names = ["Filter Options"],
            segmented_button_selected_color = "#3f5051",
            segmented_button_selected_hover_color = "#0F805A",
            text_color = "white",
            height = 600,
        )
        self.filter_options_tab.grid(
            row=0, column=0,
            sticky="n",
        )
        self.filter_options_tab.grid_remove()

        # options tab
        self.options_tab = TabsFrame(
            parent = self.filter_options_tab.tab("Filter Options"),
            tab_names = ["Visualization", "Processing"],
            segmented_button_selected_color = "#3f5051",
            segmented_button_selected_hover_color = "#0F805A",
            text_color = "white",
        )
        self.options_tab.grid(
            row=0, column=0,
            sticky="n",
        )

        # display filters tab
        self.display_tabs = TabsFrame(
            parent = self.options_tab.tab("Visualization"),
            tab_names = ["Brightness", "Color Mapping"],
            # fg_color="#b9b9b9",
            # border_width=1,
            border_color = "#979da2",
            segmented_button_selected_color="#0F805A",
            segmented_button_selected_hover_color="#3f5051",
            segmented_button_unselected_hover_color="#3f5051",
            text_color = "white",
        )
        self.display_tabs.grid(
            row=0, column=0,
            sticky="n",
        )

        # processing tabs
        self.process_tabs = TabsFrame(
            parent=self.options_tab.tab("Processing"),
            # tab_names = ["LoG", "DoG", "DoH", "Global Thr.", "Adaptive Thr."],
            tab_names=["Adaptive Thr.", "Global Thr."],
            # fg_color = "#b9b9b9",
            # border_width = 1,
            border_color = "#979da2",
            segmented_button_selected_color="#0F805A",
            segmented_button_selected_hover_color="#3f5051",
            segmented_button_unselected_hover_color="#3f5051",
            text_color = "white",
        )
        self.process_tabs.grid(
            row=0, column=0,
            sticky="n",
        )

        self.brightness_container = BrightnessGammaWidget(
            parent=self.display_tabs.tab('Brightness'),
            action_priority=12,
            coordinator=self.coordinator,
        )
        self.brightness_container.grid(
            row=0, column=0,
        )

        # spacer between two brightness methods
        ttk.Label(
            master=self.display_tabs.tab('Brightness'),
            text="",
            font=("Arial", 12),
            background="#dbdbdb",
        ).grid(
            row=1, column=0,
        )

        self.brightness_linear_container = BrightnessLinearWidget(
            parent=self.display_tabs.tab('Brightness'),
            action_priority=13,
            coordinator=self.coordinator,
        )
        self.brightness_linear_container.grid(
            row=2, column=0,
        )

        self.color_map_container = ColorMapWidget(
            parent=self.display_tabs.tab('Color Mapping'),
            action_priority=0,
            coordinator=self.coordinator,
        )
        self.color_map_container.grid(
            row=0, column=0,
        )

        self.adaptive_threshold_container = AdaptiveThresholdWidget(
            parent=self.process_tabs.tab('Adaptive Thr.'),
            action_priority=10,
            coordinator=self.coordinator,
            # fg_color="green"
        )
        self.adaptive_threshold_container.grid(
            row=0, column=0,
        )

        self.threshold_container = GlobalThresholdWidget(
            parent=self.process_tabs.tab('Global Thr.'),
            action_priority=11,
            coordinator=self.coordinator,
            # fg_color="green"
        )
        self.threshold_container.grid(
            row=0, column=0,
        )

        # # add containers to each tab
        # self.mexhat_container = MexHatWidget(
        #     parent = self.process_tabs.tab('MexHat'),
        #     action_priority = 1,
        #     coordinator = self.coordinator,
        #     # fg_color="cyan"
        # )
        # self.mexhat_container.grid(
        #     row=0, column=0,
        # )

        # # add containers to each tab
        # self.log_container = LoGWidget(
        #     parent = self.process_tabs.tab('LoG'),
        #     action_priority = 2,
        #     coordinator = self.coordinator,
        #     # fg_color="cyan"
        # )
        # self.log_container.grid(
        #     row=0, column=0,
        # )

        # # add containers to each tab
        # self.dog_container = DoGWidget(
        #     parent = self.process_tabs.tab('DoG'),
        #     action_priority = 3,
        #     coordinator = self.coordinator,
        #     # fg_color="cyan"
        # )
        # self.dog_container.grid(
        #     row=0, column=0,
        # )

        # # add containers to each tab
        # self.doh_container = DoHWidget(
        #     parent = self.process_tabs.tab('DoH'),
        #     action_priority = 4,
        #     coordinator = self.coordinator,
        #     # fg_color="cyan"
        # )
        # self.doh_container.grid(
        #     row=0, column=0,
        # )
