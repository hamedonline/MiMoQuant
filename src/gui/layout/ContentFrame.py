import customtkinter as ctk
from tkinter import ttk
from managers.Coordinator import Coordinator
from gui.widgets.Panel import Panel
from gui.widgets.TabsFrame import TabsFrame
from gui.widgets.ImageHolder import ImageHolder
from utils.entities.execution_queue import ExecutionQueue



class ContentFrame(ttk.Frame):
    __slots__ = [
        'parent',
        'coordinator',
        'display_manager',
        'state_manager',
        'action_manager',
        'annotation_manager',
        'analysis_manager',
        'layout_manager',
        'file_manager',
        'style',
        'roi_tab',
        'roi_sections_tab',
        'canvas_size',
        'tool_panels_height_size',
        'label_of_the_puncts',
        'label_of_the_branchings',
        'roi_holder',
        'manual_analysis_holder',
        'annotation_holder',
        'load_commands',
        'unload_commands',
    ]

    def __init__(self, parent: ttk.Frame, coordinator: Coordinator, canvas_size, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.coordinator = coordinator
        self.display_manager = self.coordinator.ask_for_manager('display')
        self.state_manager = self.coordinator.ask_for_manager('state')
        self.action_manager = self.coordinator.ask_for_manager('action')
        self.annotation_manager = self.coordinator.ask_for_manager('annotation')
        self.analysis_manager = self.coordinator.ask_for_manager('analysis')
        self.layout_manager = self.coordinator.ask_for_manager('layout')
        self.file_manager = self.coordinator.ask_for_manager('file')
        self.canvas_size: tuple[int, int] = canvas_size
        self.tool_panels_height_size = 54
        self.label_of_the_puncts = self.coordinator.get_global_label_of_the_puncts()
        self.label_of_the_branchings = self.coordinator.get_global_label_of_the_branchings()

        self.style = ttk.Style(self)
        self.style.configure("content_frame.TFrame")
        self.configure(style="content_frame.TFrame")

        # define grid for the content frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)

        self.create_widgets()


    def create_widgets(self):
        # region of interest (ROI) tab
        self.roi_tab = TabsFrame(
            parent = self,
            tab_names = ["Region of Interest"],
            segmented_button_selected_color = "#3f5051",
            segmented_button_selected_hover_color = "#0F805A",
            text_color="white",
        )
        self.roi_tab.grid(
            row=1, column=0,
            sticky="n",
        )

        # roi sections tab
        self.roi_sections_tab = TabsFrame(
            parent = self.roi_tab.tab("Region of Interest"),
            tab_names=["Auto-Analysis", "Annotation", "Filter-Output"],
            segmented_button_selected_color="#0F805A",
            segmented_button_selected_hover_color="#3f5051",
            segmented_button_unselected_hover_color="#3f5051",
            text_color="white",
            width = self.canvas_size[0] + 20,
            height = self.canvas_size[1] + 48,
        )
        self.roi_sections_tab.grid(
            row=0, column=0,
            sticky="n",
        )

        # main roi holder
        toggle_command_auto_analysis = ExecutionQueue(
            (self.display_manager.toggle_image_auto_analysis, (), {}, 0),
        )
        self.roi_holder = ImageHolder(
            parent = self.roi_sections_tab.tab("Auto-Analysis"),
            canvas_args={
                'dimension': self.canvas_size,
                # 'bg': "#bacedb",
                'bg': "#dbdbdb",
                # 'padding': 5,
            },
            has_toggle_button=True,
            toggle_command=toggle_command_auto_analysis,
            has_save_button=True,
            save_command=ExecutionQueue(
                (self.file_manager.save_image_via_dialog, (), lambda: {
                    'image_array': self.display_manager.get_auto_processed_image().get_image_array(),
                    'window_title': "Save auto-analysis image...",
                    'save_dir': self.display_manager.get_roi_image().get_file_dir(),
                    'file_name': self.display_manager.get_roi_image().get_file_name(),
                    'additional_prefix': self.file_manager.get_identifier_for_cutout_images(),
                    'additional_postfix': "_auto-analysis",
                }, 0)
            ),
            color_mode='grayscale',
            open_button_label="Load Image",
            toggle_button_tooltip="Toggle Detected Object Boxes"
        )
        self.roi_holder.hide_toggle_button()
        self.roi_holder.hide_save_button()
        self.roi_holder.grid(row=0, column=0)
        self.display_manager.register_roi_holder(self.roi_holder)

        self.load_commands = ExecutionQueue(
            (self.display_manager.prepare_and_set_roi_zone_images, (), {}, 0),
            (self.annotation_manager.register_annotation_proceedings, (), {}, 0),
            (self.annotation_manager.clear_annotation_set, (), {}, 0),
            (self.analysis_manager.clear_analysis, (), {}, 0),
            (self.coordinator.reset_all_counting_stats, (), {}, 0),
            (self.action_manager.clear_out_action_queue, (), {}, 0),
            (self.state_manager.set_roi_as_loaded_from_file, (), {}, 0),
            (self.state_manager.set_roi_as_assigned, (), {}, 0),
            (self.layout_manager.disable_button_transfer_to_annotations, (), {}, 0),
            (self.layout_manager.hide_button_toggle_auto_analysis, (), {}, 0),
            (self.layout_manager.hide_button_save_auto_analysis, (), {}, 0),
            (self.layout_manager.hide_button_toggle_annotations, (), {}, 0),
            (self.layout_manager.hide_button_toggle_filter_output, (), {}, 0),
            (self.layout_manager.show_tooling_panels, (), {}, 0),
            (self.layout_manager.show_filter_options_panel, (), {}, 0),
            (self.layout_manager.show_report_panel, (), {}, 0),
            (lambda: self.layout_manager.show_auto_analysis_profile_panel(), (), {}, 0),
            (self.annotation_manager.check_for_annotation_file, (), {}, 0), # important to be the last command
        )
        self.roi_holder.register_load_command(self.load_commands)

        self.unload_commands = ExecutionQueue(
            (self.display_manager.clear_other_holders, (), {}, 0),
            (self.display_manager.evacuate_roi_zone_images, (), {}, 0),
            # (self.display_manager.evacuate_roi_zone_holders, (), {}, 0),
            (self.coordinator.reset_all_counting_stats, (), {}, 0),
            (self.annotation_manager.clear_annotation_set, (), {}, 0),
            (self.state_manager.unset_roi_as_loaded_from_file, (), {}, 0),
            (self.state_manager.unset_roi_as_assigned, (), {}, 0),
            (self.state_manager.unset_all_images_from_display, (), {}, 0),
            (self.layout_manager.hide_tooling_panels, (), {}, 0),
            (self.layout_manager.hide_filter_options_panel, (), {}, 0),
            (self.layout_manager.hide_report_panel, (), {}, 0),
            (lambda: self.layout_manager.hide_auto_analysis_profile_panel(), (), {}, 0),
        )
        self.roi_holder.register_unload_command(self.unload_commands)

        # auto-analysis tools panel
        self.auto_analysis_tools_panel = Panel(
            parent=self.roi_sections_tab.tab("Auto-Analysis"),
            num_rows=1, num_cols=4,
            fg_color="#cfcfcf",
            height=self.tool_panels_height_size,
        )
        self.auto_analysis_tools_panel.grid(
            row=1, column=0,
            pady=4, ipady=8, padx=4, ipadx=8,
            sticky="nswe",
        )
        self.auto_analysis_tools_panel.grid_propagate(False) # for a fixed size panel
        self.auto_analysis_tools_panel.grid_remove()

        ctk.CTkLabel(
            master = self.auto_analysis_tools_panel,
            text=""
        ).grid(
            row=0, column=0, sticky="w",
            padx=1, pady=4,
        )

        self.auto_analysis_button = ctk.CTkButton(
            master = self.auto_analysis_tools_panel,
            text = "Perform Automatic Analysis",
            cursor = "hand2",
            command = self.analysis_manager.perform_analysis,
            fg_color = "#3f5051",
            hover_color = "#0F805A",
            text_color = "white",
        )
        self.auto_analysis_button.grid(row=0, column=1, sticky="w")

        self.transform_to_annotations_button = ctk.CTkButton(
            master=self.auto_analysis_tools_panel,
            text = "Transfer Analysis to Annotation ➜",
            cursor = "hand2",
            command = self.analysis_manager.transform_to_annotations,
            fg_color = "#3f5051",
            hover_color = "#0F805A",
            text_color = "white",
        )
        self.transform_to_annotations_button.grid(row=0, column=2, sticky="e")
        self.transform_to_annotations_button.configure(state="disabled")

        ctk.CTkLabel(
            master = self.auto_analysis_tools_panel,
            text=""
        ).grid(
            row=0, column=3, sticky="e",
            padx=1, pady=4,
        )


        # annotation holder
        toggle_command_annotation = ExecutionQueue(
            (self.display_manager.toggle_image_annotation, (), {}, 0),
        )
        self.annotation_holder = ImageHolder(
            parent = self.roi_sections_tab.tab("Annotation"),
            canvas_args={
                'dimension': self.canvas_size,
                # 'bg': "#bacedb",
                'bg': "#dbdbdb",
                # 'padding': 5,
            },
            has_open_button = False,
            has_close_button = False,
            has_toggle_button = True,
            # has_save_button=True,
            toggle_command=toggle_command_annotation,
            color_mode='grayscale',
            toggle_button_tooltip="Toggle Annotation Objects"
        )
        self.annotation_holder.hide_toggle_button()
        self.annotation_holder.grid(row=0, column=0)
        self.display_manager.register_annotation_holder(self.annotation_holder)

        # annotation tools panel
        self.annotation_tools_panel = Panel(
            parent=self.roi_sections_tab.tab("Annotation"),
            num_rows=1, num_cols=6,
            fg_color="#cfcfcf",
            height=self.tool_panels_height_size,
        )
        self.annotation_tools_panel.grid(
            row=1, column=0,
            pady=4, ipady=8, padx=4, ipadx=8,
            sticky="nswe",
        )
        self.annotation_tools_panel.grid_propagate(False) # for a fixed size panel
        self.annotation_tools_panel.grid_remove()

        self.annotation_type_label = ctk.CTkLabel(
            master=self.annotation_tools_panel,
            text = "Annotation Object:"
        )
        self.annotation_type_label.grid(
            row=0, column=0, sticky="e",
            padx=12, pady=5,
        )
        self.annotation_type_option = ctk.StringVar(value=self.label_of_the_puncts)
        self.annotation_type = ctk.CTkOptionMenu(
            master = self.annotation_tools_panel,
            values = [self.label_of_the_puncts, self.label_of_the_branchings],
            variable = self.annotation_type_option,
            command = self.set_annotation_type,
            fg_color = "#3f5051",
            button_color = "#0F805A",
            button_hover_color = "#15ba85",
        )
        self.annotation_type.grid(
            row=0, column=1, sticky="w",
            padx=12, pady=5,
        )

        self.clear_annotations_button = ctk.CTkButton(
            master = self.annotation_tools_panel,
            text = "Clear all annotations?",
            cursor = "hand2",
            command = self.annotation_manager.clear_annotations,
            fg_color = "#3f5051",
            hover_color = "#0F805A",
            text_color = "white",
        )
        self.clear_annotations_button.grid(row=0, column=2, sticky="w")

        ctk.CTkLabel(
            master=self.annotation_tools_panel,
            text=""
        ).grid(
            row=0, column=3, sticky="e",
            padx=1, pady=4,
        )

        self.export_button = ctk.CTkButton(
            master = self.annotation_tools_panel,
            text = "✨ Export",
            cursor = "hand2",
            command=self.annotation_manager.trigger_export,
            fg_color = "#3f5051",
            hover_color = "#0F805A",
            text_color = "white",
            width=80,
        )
        self.export_button.grid(row=0, column=4, sticky="e")

        ctk.CTkLabel(
            master=self.annotation_tools_panel,
            text=""
        ).grid(
            row=0, column=5, sticky="e",
            padx=1, pady=4,
        )


        # manual-analysis holder
        toggle_command_manual_analysis = ExecutionQueue(
            (self.display_manager.toggle_image_manual_analysis, (), {}, 0),
        )
        self.manual_analysis_holder = ImageHolder(
            parent = self.roi_sections_tab.tab("Filter-Output"),
            canvas_args={
                'dimension': self.canvas_size,
                # 'bg': "#bacedb",
                'bg': "#dbdbdb",
                # 'padding': 5,
            },
            has_open_button = False,
            has_close_button = False,
            has_toggle_button = True,
            toggle_command=toggle_command_manual_analysis,
            color_mode='grayscale',
            toggle_button_tooltip="Toggle Filter/Original View"
        )
        self.manual_analysis_holder.hide_toggle_button()
        self.manual_analysis_holder.grid(row=0, column=0)
        self.display_manager.register_manual_analysis_holder(self.manual_analysis_holder)

        # manual-analysis tools panel
        self.manual_analysis_tools_panel = Panel(
            parent=self.roi_sections_tab.tab("Filter-Output"),
            num_rows=1, num_cols=1,
            fg_color="#cfcfcf",
            height=self.tool_panels_height_size,
        )
        self.manual_analysis_tools_panel.grid(
            row=1, column=0,
            pady=4, ipady=8, padx=4, ipadx=8,
            sticky="nswe",
        )
        self.manual_analysis_tools_panel.grid_propagate(False) # for a fixed size panel
        self.manual_analysis_tools_panel.grid_remove()

        ctk.CTkLabel(
            master=self.manual_analysis_tools_panel,
            text=""
        ).grid(
            row=0, column=0, sticky="nswe",
            padx=1, pady=4,
        )


######################################################
    def set_annotation_type(self, choice):
        if choice == self.label_of_the_puncts:
            self.coordinator.retrieve('annotation_type').set(0)
        elif choice == self.label_of_the_branchings:
            self.coordinator.retrieve('annotation_type').set(1)
        else:
            raise ValueError(f"Invalid annotation type. Must be either {self.label_of_the_puncts} or {self.label_of_the_branchings}.")
