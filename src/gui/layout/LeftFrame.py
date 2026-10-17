import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from managers.Coordinator import Coordinator
from gui.widgets.TabsFrame import TabsFrame
from gui.widgets.ImageHolder import ImageHolder
from gui.widgets.ValueSlider import ValueSlider
from gui.widgets.Panel import Panel
from gui.layout.CutoutWindow import CutoutWindow
from utils.entities.execution_queue import ExecutionQueue


class LeftFrame(ttk.Frame):
    __slots__ = [
        'parent',
        'coordinator',
        'display_manager',
        'state_manager',
        'annotation_manager',
        'action_manager',
        'analysis_manager',
        'layout_manager',
        'label_of_the_puncts',
        'label_of_the_branchings',
        'style',
        'wsi_tab',
        'source_holder',
        'source_holder_load_commands',
        'source_holder_unload_commands',
        'interaction_tabs',
        'crop_window',
    ]

    def __init__(self, parent: ttk.Frame, coordinator: Coordinator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent,
        self.coordinator = coordinator
        self.display_manager = self.coordinator.ask_for_manager('display')
        self.state_manager = self.coordinator.ask_for_manager('state')
        self.annotation_manager = self.coordinator.ask_for_manager('annotation')
        self.action_manager = self.coordinator.ask_for_manager('action')
        self.analysis_manager = self.coordinator.ask_for_manager('analysis')
        self.layout_manager = self.coordinator.ask_for_manager('layout')
        self.label_of_the_puncts = self.coordinator.get_global_label_of_the_puncts()
        self.label_of_the_branchings = self.coordinator.get_global_label_of_the_branchings()

        self.style = ttk.Style(self)
        self.style.configure(
            "left_frame.TFrame",
            # background="red"
        )
        self.configure(style="left_frame.TFrame")

        # define grid for the left frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0,1,2,3), weight=1)

        self.create_widgets()


    def create_widgets(self):

        # whole slide image (WSI) tab
        self.wsi_tab = TabsFrame(
            parent = self,
            tab_names = ["Whole Slide Image"],
            segmented_button_selected_color="#3f5051",
            segmented_button_selected_hover_color="#0F805A",
            text_color="white",
            # height=200,
        )
        self.wsi_tab.grid(
            row=1, column=0,
            sticky="n",
        )

        # whole slide image holder
        self.source_holder = ImageHolder(
            parent = self.wsi_tab.tab("Whole Slide Image"),
            canvas_args = {
                "dimension": (300, 225),
                # "bg": "#bacedb",
                "bg": "#dbdbdb",
            },
            color_mode="grayscale",
            open_button_label="Load Image",
        )
        self.source_holder.grid(row=0, column=0)
        self.display_manager.register_source_holder(self.source_holder)

        self.source_holder_load_commands = ExecutionQueue(
            (self.source_holder.get_image_canvas().bind, ("<Button-1>", self.open_cutout_window), {}, 0),
            (self.display_manager.prepare_and_set_source_image, (), {}, 0),
            (self.state_manager.set_wsi_as_assigned, (), {}, 0),
        )
        self.source_holder.register_load_command(self.source_holder_load_commands)

        self.source_holder_unload_commands = ExecutionQueue(
            (self.display_manager.evacuate_source_image, (), {}, 0),
            # (self.display_manager.evacuate_source_holder, (), {}, 0),
            (self.state_manager.unset_wsi_as_assigned, (), {}, 0),
        )
        self.source_holder.register_unload_command(self.source_holder_unload_commands)


        # report panel tab
        self.report_tab = TabsFrame(
            parent = self,
            tab_names = ["Report Panel"],
            num_rows=4,
            num_cols=4,
            segmented_button_selected_color="#3f5051",
            segmented_button_selected_hover_color="#0F805A",
            text_color="white",
        )
        self.report_tab.grid(
            row=2, column=0,
            sticky="n",
        )
        self.report_tab.grid_remove()

        # spacer row
        ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text="",
            font=("Arial", 12),
            justify=tk.CENTER,
            foreground="#3f5051",
            background="#dbdbdb",
        ).grid(row=0, column=0)

        ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text="Auto-Analysis",
            font=("Arial", 12),
            justify=tk.CENTER,
            foreground="#3f5051",
            background="#dbdbdb",
        ).grid(row=1, column=1)

        ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text="Annotated",
            font=("Arial", 12),
            justify=tk.CENTER,
            foreground="#3f5051",
            background="#dbdbdb",
        ).grid(row=1, column=3)

        ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text= " "*8,
            font=("Arial", 12),
            justify=tk.CENTER,
            foreground="#3f5051",
            background="#dbdbdb",
        ).grid(row=1, column=2)

        ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text=self.label_of_the_puncts,
            font=("Arial", 12, "bold"),
            justify=tk.CENTER,
            foreground="#3f5051",
            background="#dbdbdb",
        ).grid(row=2, column=0)

        ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text=self.label_of_the_branchings,
            font=("Arial", 12, "bold"),
            justify=tk.CENTER,
            foreground="#3f5051",
            background="#dbdbdb",
        ).grid(row=3, column=0)

        self.count_dots_annotated = ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text=self.coordinator.retrieve('count_stats')['annotated']['dots'],
            font=("Arial", 18, "bold"),
            justify=tk.CENTER,
            foreground="#0F805A",
            background="#dbdbdb",
            textvariable=self.coordinator.retrieve('count_stats')['annotated']['dots'],
        ).grid(row=2, column=3)

        self.count_branches_annotated = ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text=self.coordinator.retrieve('count_stats')['annotated']['branches'],
            # text="0",
            font=("Arial", 18, "bold"),
            justify=tk.CENTER,
            foreground="#0F805A",
            background="#dbdbdb",
            textvariable=self.coordinator.retrieve('count_stats')['annotated']['branches'],
        ).grid(row=3, column=3)

        self.count_dots_auto = ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text=self.coordinator.retrieve('count_stats')['auto']['dots'],
            font=("Arial", 18, "bold"),
            justify=tk.CENTER,
            foreground="#0F805A",
            background="#dbdbdb",
            textvariable=self.coordinator.retrieve('count_stats')['auto']['dots'],
        ).grid(row=2, column=1)

        self.count_branches_auto = ttk.Label(
            master=self.report_tab.tab("Report Panel"),
            text=self.coordinator.retrieve('count_stats')['auto']['branches'],
            # text="0",
            font=("Arial", 18, "bold"),
            justify=tk.CENTER,
            foreground="#0F805A",
            background="#dbdbdb",
            textvariable=self.coordinator.retrieve('count_stats')['auto']['branches'],
        ).grid(row=3, column=1)


        # auto-analysis profile panel tab
        self.analysis_profile_tab = TabsFrame(
            parent = self,
            tab_names = ["Auto-Analysis Profile"],
            num_rows=1,
            num_cols=1,
            segmented_button_selected_color="#3f5051",
            segmented_button_selected_hover_color="#0F805A",
            text_color="white",
        )
        self.analysis_profile_tab.grid(
            row=3, column=0,
            sticky="n",
        )
        self.analysis_profile_tab.grid_remove()

        # confidence threshold adjustment tab
        slider_color = "#3f5051"
        self.slider_padding_config = {'padx':5, 'pady':2, 'ipadx':0, 'ipady':0}
        self.confidence_threshold_tab = TabsFrame(
            parent = self.analysis_profile_tab.tab("Auto-Analysis Profile"),
            tab_names = ["Conf. Thr."],
            num_rows=1,
            num_cols=1,
            segmented_button_selected_color="#3f5051",
            segmented_button_selected_hover_color="#0F805A",
            text_color="white",
        )
        self.confidence_threshold_tab.grid(
            row=0, column=0,
            sticky="n",
        )
        self.thresholds_panel = Panel(
            parent=self.confidence_threshold_tab.tab("Conf. Thr."),
            num_rows=4, num_cols=1,
            fg_color="#cfcfcf",
        )
        self.thresholds_panel.grid(
            row=0, column=0,
            pady=4, ipady=8, padx=4, ipadx=8,
            sticky="ew"
        )
        tab_frame = self.confidence_threshold_tab.tab("Conf. Thr.")
        tab_frame.columnconfigure(0, weight=1)

        self.slider_conf_threshold_dots = ValueSlider(
            parent = self.thresholds_panel,
            label = self.label_of_the_puncts + ":",
            value_range = (0.1, 0.6),
            value_object = self.coordinator.get_obj_conf_threshold_dots(),
            step_precision = 0.01,
            fg_color = slider_color,
        )
        self.slider_conf_threshold_dots.grid(row=0, column=0, **self.slider_padding_config)
        self.slider_conf_threshold_branches = ValueSlider(
            parent = self.thresholds_panel,
            label = self.label_of_the_branchings + ":",
            value_range = (0.1, 0.6),
            value_object = self.coordinator.get_obj_conf_threshold_branches(),
            step_precision = 0.01,
            fg_color = slider_color,
        )
        self.slider_conf_threshold_branches.grid(row=1, column=0, **self.slider_padding_config)

        ctk.CTkLabel(
            master = self.thresholds_panel,
            text="↑ confidence : ↓ detections",
        ).grid(
            row=2, column=0, sticky="w",
            padx=12, pady=5,
        )
        ctk.CTkButton(
            master = self.thresholds_panel,
            text = "Reset",
            cursor = "hand2",
            command = lambda: self._reset_confidence_values_via_button(),
            fg_color = "#3f5051",
            hover_color = "#0F805A",
            text_color = "white",
            width=50,
        ).grid(
            row=2, column=0, sticky="e",
            padx=12, pady=5
        )

        # trace changes in the slider values
        self.coordinator.get_obj_conf_threshold_dots().trace_add("write", self.analysis_manager.check_and_update_confidence_threshold)
        self.coordinator.get_obj_conf_threshold_branches().trace_add("write", self.analysis_manager.check_and_update_confidence_threshold)


    def _reset_confidence_values_via_button(self):
        self.coordinator.reset_var_conf_threshold_dots()
        self.coordinator.reset_var_conf_threshold_branches()
        self.slider_conf_threshold_dots.update_via_tracing()
        self.slider_conf_threshold_branches.update_via_tracing()


    def open_cutout_window(self, event):
        self.crop_window = CutoutWindow(
            window_title = self.coordinator.retrieve('window_title_cutout'),
            coordinator = self.coordinator
        )
        # self.crop_window.mainloop()
        print("Cutout window opened.")
