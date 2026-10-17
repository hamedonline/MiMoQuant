import customtkinter as ctk
import tkinter as tk
import platform

from tkinter import messagebox
from managers.Coordinator import Coordinator
from gui.widgets.TabsFrame import TabsFrame
from gui.widgets.ImageHolder import ImageHolder
from gui.widgets.Panel import Panel
from gui.widgets.ValueSlider import ValueSlider
from utils.entities.data_storage import DataStorage



class CutoutWindow(tk.Toplevel):
    def __init__(
        self,
        window_title: str,
        coordinator: Coordinator,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.coordinator = coordinator
        self.display_manager = self.coordinator.ask_for_manager('display')
        self.state_manager = self.coordinator.ask_for_manager('state')
        self.annotation_manager = self.coordinator.ask_for_manager('annotation')
        self.action_manager = self.coordinator.ask_for_manager('action')
        self.layout_manager = self.coordinator.ask_for_manager('layout')
        self.analysis_manager = self.coordinator.ask_for_manager('analysis')
        self.roi_size = self.coordinator.get_var_cutout_size()

        # window setup
        self.title(window_title)
        if platform.system() == "Windows":
            self.state('zoomed')
        else:
            self.update_idletasks()
            self.geometry("{}x{}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        self.deiconify()
        self.resizable(width=False, height=False)

        # grid setup
        self.columnconfigure(0, weight=9, uniform="layout columns")
        self.columnconfigure(1, weight=3, uniform="layout columns")
        self.rowconfigure(0, weight=1)
        self.grid()

        # initializations
        self.update_idletasks()
        self.canvas_dimension = (self.winfo_width()*(9/(9+3)), self.winfo_height())

        self.crop_storage = DataStorage()
        self._create_widgets()
        self.crop_size = self._calculate_crop_size()
        self.crop_border_size = 3
        self._bind_initial_events()
        # self.mainloop()


    def _create_widgets(self):
        self.image_holder = ImageHolder(
            parent=self,
            canvas_args={
                'dimension': self.canvas_dimension,
                # 'bg': "#bacedb",
            },
            has_open_button=False,
            has_close_button=False,
            color_mode='grayscale',
        )
        self.image_holder.grid(row=0, column=0, sticky="n")
        self.image_holder.display_image(
            image = self.display_manager.get_source_image()
        )

        # right frame (holds ROI option & info panels)
        self.right_frame = Panel(
            parent=self,
            num_rows=3, num_cols=1,
            fg_color="#f0f0f0",
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        panel_padding_config = {'padx': 2, 'pady': 2, 'ipadx': 4, 'ipady': 4}


        # side info tab & panel
        self.info_tab = TabsFrame(
            parent=self.right_frame,
            tab_names=["WSI Info Panel"],
            num_rows=1, num_cols=1,
            segmented_button_selected_color="#3f5051",
            segmented_button_selected_hover_color="#0F805A",
            text_color="white",
        )
        self.info_tab.grid(
            row=0, column=0,
            # sticky="s",
        )
        self.info_tab.tab("WSI Info Panel").columnconfigure(0, weight=1)
        self.info_panel = Panel(
            parent=self.info_tab.tab("WSI Info Panel"),
            num_rows=2, num_cols=1,
        )
        self.info_panel.grid(
            row=0, column=0,
            **panel_padding_config,
            sticky="nsew"
        )
        self.file_name_panel = Panel(
            parent=self.info_panel,
            num_rows=2, num_cols=2,
            fg_color="#cfcfcf",
        )
        self.file_name_panel.grid(
            row=0, column=0,
            **panel_padding_config,
            sticky="ew"
        )
        self.file_name_label = ctk.CTkLabel(
            master=self.file_name_panel,
            text="File Name:",
            font=("Arial", 12, "bold"),
        )
        self.file_name_label.grid(
            row=0, column=0,
            padx=12, pady=5,
            sticky="w"
        )
        self.file_name_value_label = ctk.CTkLabel(
            master=self.file_name_panel,
            text=self.display_manager.get_source_image().get_file_name(),
            wraplength=250
        )
        self.file_name_value_label.grid(
            row=1, column=0,
            padx=12, pady=5,
            sticky="w", columnspan=2
        )
        self.file_size_panel = Panel(
            parent=self.info_panel,
            num_rows=2, num_cols=2,
            fg_color="#cfcfcf",
        )
        self.file_size_panel.grid(
            row=1, column=0,
            **panel_padding_config,
            sticky="ew"
        )
        self.file_size_label = ctk.CTkLabel(
            master=self.file_size_panel,
            text="Size Info:",
            font=("Arial", 12, "bold"),
        )
        self.file_size_label.grid(
            row=0, column=0,
            padx=12, pady=5,
            sticky="w"
        )
        self.file_size_value_label = ctk.CTkLabel(
            master=self.file_size_panel,
            text=self._generate_file_size_info(),
            wraplength=250
        )
        self.file_size_value_label.grid(
            row=1, column=0,
            padx=12, pady=5,
            sticky="w", columnspan=2,
        )


        # ROI options tab
        self.roi_options_tab = TabsFrame(
            parent=self.right_frame,
            tab_names=["ROI Options"],
            segmented_button_selected_color="#3f5051",
            segmented_button_selected_hover_color="#0F805A",
            text_color="white",
        )
        self.roi_options_tab.grid(
            row=1, column=0,
            sticky="n",
        )

        # ROI size panel
        self.panel_sizing = Panel(
            parent=self.roi_options_tab.tab("ROI Options"),
            num_rows=4, num_cols=1,
            fg_color="#cfcfcf",
        )
        self.panel_sizing.grid(
            row=0, column=0,
            **panel_padding_config,
        )
        self.sizing_label = ctk.CTkLabel(
            master = self.panel_sizing,
            text = "ROI Box Size (in pixels)"
        )
        self.sizing_label.grid(
            row=0, column=0, sticky="w",
            padx=12, pady=5,
        )
        # define slider configurations
        slider_color = "#3f5051"
        slider_padding_config = {'padx': 3, 'pady': 3, 'ipadx': 3, 'ipady': 3}
        self.width_slider = ValueSlider(
            parent = self.panel_sizing,
            label = "Width:",
            value_range = (100, 500),
            value_object = self.coordinator.get_obj_roi_width(),
            step_precision = 25,
            fg_color = slider_color,
        )
        self.width_slider.grid(row=1, column=0, **slider_padding_config)
        self.height_slider = ValueSlider(
            parent = self.panel_sizing,
            label = "Height:",
            value_range = (100, 500),
            value_object = self.coordinator.get_obj_roi_height(),
            step_precision = 25,
            fg_color = slider_color,
        )
        self.height_slider.grid(row=2, column=0, **slider_padding_config)
        # preset crop size buttons
        self.preset_crop_sizes_panel = Panel(
            parent=self.panel_sizing,
            num_rows=1, num_cols=3,
            fg_color="#cfcfcf",
        )
        self.preset_crop_sizes_panel.grid(
            row=3, column=0,
            **panel_padding_config,
            sticky="ew"
        )
        self.preset_crop_size_150_button = ctk.CTkButton(
            master = self.preset_crop_sizes_panel,
            text = "150 x 150",
            cursor = "hand2",
            command = lambda: self._set_cropping_size_via_button(150, 150),
            fg_color = "#3f5051",
            hover_color = "#0F805A",
            text_color = "white",
            width=50,
        )
        self.preset_crop_size_150_button.grid(row=0, column=0, )
        self.preset_crop_size_300_button = ctk.CTkButton(
            master = self.preset_crop_sizes_panel,
            text = "300 x 300",
            cursor = "hand2",
            command = lambda: self._set_cropping_size_via_button(300, 300),
            fg_color = "#3f5051",
            hover_color = "#0F805A",
            text_color = "white",
            width=50,
        )
        self.preset_crop_size_300_button.grid(row=0, column=1, )
        self.preset_crop_size_500_button = ctk.CTkButton(
            master = self.preset_crop_sizes_panel,
            text = "500 x 500",
            cursor = "hand2",
            command = lambda: self._set_cropping_size_via_button(500, 500),
            fg_color = "#3f5051",
            hover_color = "#0F805A",
            text_color = "white",
            width=50,
        )
        self.preset_crop_size_500_button.grid(row=0, column=2, )

        # trace changes in the slider values
        self.roi_width_trace_id = self.coordinator.get_obj_roi_width().trace_add("write", self._apply_cropping_size_change)
        self.roi_height_trace_id = self.coordinator.get_obj_roi_height().trace_add("write", self._apply_cropping_size_change)


        # shortcuts tab & panel
        self.shortcuts_tab = TabsFrame(
            parent=self.right_frame,
            tab_names=["Shortcuts Guide"],
            segmented_button_selected_color="#3f5051",
            segmented_button_selected_hover_color="#0F805A",
            text_color="white",
        )
        self.shortcuts_tab.grid(
            row=2, column=0,
            sticky="s",
        )
        self.shortcuts_tab.tab("Shortcuts Guide").columnconfigure(0, weight=1)
        self.shortcut_info_panel = Panel(
            parent=self.shortcuts_tab.tab("Shortcuts Guide"),
            num_rows=6, num_cols=1,
            fg_color="#cfcfcf",
        )
        self.shortcut_info_panel.grid(
            row=2, column=0,
            **panel_padding_config,
        )
        self.shortcut_info_label = ctk.CTkLabel(
            master=self.shortcut_info_panel,
            text="Mouse & keyboard shortcuts:",
            font=("Arial", 12, "bold"),
        )
        self.shortcut_info_label.grid(
            row=0, column=0,
            padx=12, pady=5,
            sticky="w"
        )
        self.shortcuts_info = [
            "Left-click: Place/Move ROI box",
            "Drag (hold left-click): Move ROI box",
            "Arrow keys: Fine-tune ROI box position",
            "Right-click (inside ROI box): Remove ROI box",
            "Middle-click | <SPACE> | <ENTER> | <C>: Finalize cutout",
            "<ESC>: Close window (crop is applied if ROI box exists)",
        ]
        for i, shortcut in enumerate(self.shortcuts_info):
            lbl = ctk.CTkLabel(
                master=self.shortcut_info_panel,
                text=shortcut,
                font=("Arial", 11),
            )
            lbl.grid(
                row=i+1, column=0,
                padx=8, pady=2,
                sticky="w"
            )



    def _generate_file_size_info(self) -> str:
        img_width, img_height = self.display_manager.get_source_image().get_dimensions()
        img_size_in_bytes = self.display_manager.get_source_image().get_file_size()
        return f"{img_width} x {img_height} {' '*4} {img_size_in_bytes/1024:.1f} KB"

    def _set_cropping_size_via_button(self, width: int, height: int):
        self.coordinator.set_var_cutout_size(width, height)
        self.width_slider.update_via_tracing()
        self.height_slider.update_via_tracing()
        self._apply_cropping_size_change()

    def _apply_cropping_size_change(self, *args):
        # update roi size
        self.roi_size = self.coordinator.get_var_cutout_size()
        # update crop size
        self.crop_size = self._calculate_crop_size()
        # resize the rectangle on the canvas (if it exists)
        if self.crop_storage.key_exists('cutout'):
            center = self.crop_storage.get('cutout')['center']
            _, start, end = self._calculate_cutout_coordinates(event=type('mock_event', (object,), {'x': center[0], 'y': center[1]}))
            self._update_cutout_coordinates(start, end, center)

    def _bind_initial_events(self):
        self.image_holder.get_image_canvas().bind("<Button-1>", self._on_click)
        self.image_holder.get_image_canvas().configure(cursor="target")
        self.bind("<Escape>", self._on_closing)
        self.protocol("WM_DELETE_WINDOW", self._on_closing) # handle manual window close (clicking on the "X" button)
        if self.display_manager.has_key('last_cutout'):
            self._restore_cutout()

    def _restore_cutout(self, event=None):
        cutout = self.display_manager.retrieve('last_cutout')
        self.crop_storage.add(cutout=cutout)
        self.image_holder.get_image_canvas().create_rectangle(
            cutout['start'][0], cutout['start'][1], cutout['end'][0], cutout['end'][1],
            outline = "limegreen",
            width = self.crop_border_size,
            # dash = (10, 10),
        )
        self._bind_interaction_events(event)

    def _bind_arrow_keys(self, event):
        self.bind("<Left>", lambda event: self._move_rectangle(direction='left'))
        self.bind("<Right>", lambda event: self._move_rectangle(direction='right'))
        self.bind("<Up>", lambda event: self._move_rectangle(direction='up'))
        self.bind("<Down>", lambda event: self._move_rectangle(direction='down'))

    def _unbind_arrow_keys(self):
        self.unbind("<Left>")
        self.unbind("<Right>")
        self.unbind("<Up>")
        self.unbind("<Down>")

    def _bind_cutout_keys(self):
        # bind window close actions on "Space"/"Enter"/"c" key press
        self.bind("<space>", self._on_closing)
        self.bind("<Return>", self._on_closing)
        self.bind("c", self._on_closing)

    def _unbind_cutout_keys(self):
        self.unbind("<space>")
        self.unbind("<Return>")
        self.unbind("c")

    def _bind_middle_right_click(self):
        self.image_holder.get_image_canvas().bind("<Button-2>", self._on_closing)
        self.image_holder.get_image_canvas().bind("<Button-3>", self._on_right_click)

    def _unbind_middle_right_click(self):
        self.image_holder.get_image_canvas().unbind("<Button-2>")
        self.image_holder.get_image_canvas().unbind("<Button-3>")

    def _bind_interaction_events(self, event):
        # bind drag event
        self.image_holder.get_image_canvas().bind("<B1-Motion>", self._on_drag)
        # bind arrow key events for fine-tuning the ROI rectangle position
        self._bind_arrow_keys(event)
        # bind middle & right mouse click events for finalizing the cutout
        self._bind_middle_right_click()
        # bind cutout keys
        self._bind_cutout_keys()


    def _calculate_crop_size(self):
        scale_ratio_width, scale_ratio_height = self.image_holder.get_image_entity().get_resize_ratio() # type: ignore
        roi_size_width, roi_size_height = self.roi_size
        return (int(round(roi_size_width * scale_ratio_width)), int(round(roi_size_height * scale_ratio_height)))


    def _cropping_ROI_exists(self):
        return self.crop_storage.key_exists('cutout')


    def _cropping_ROI_is_within_image_boundaries(self):
        crop_start, crop_end, _ = self._get_cutout_coordinates()
        resized_img_top_left, resized_img_bottom_right = self._get_resized_image_coordinates()

        # check if the crop rectangle goes out of the the displayed image on the canvas
        if crop_start[0] < resized_img_top_left[0] or crop_start[1] < resized_img_top_left[1] or \
            crop_end[0] > resized_img_bottom_right[0] or crop_end[1] > resized_img_bottom_right[1]:
            return False
        return True


    def _on_closing(self, event=None):
        # remove tracers of roi size values
        try:
            if hasattr(self, 'roi_width_trace_id') and self.roi_width_trace_id:
                self.coordinator.get_obj_roi_width().trace_vdelete("w", self.roi_width_trace_id)
            if hasattr(self, 'roi_height_trace_id') and self.roi_height_trace_id:
                self.coordinator.get_obj_roi_height().trace_vdelete("w", self.roi_height_trace_id)
        except tk.TclError:
            # ignore the error if the trace can't be deleted (trace doesn't exist probably)
            pass

        if not self._cropping_ROI_exists():
            self.destroy()
            self.display_manager.get_source_holder().display_image(self.display_manager.get_source_image())
            return

        if not self._cropping_ROI_is_within_image_boundaries():
            # pop up a warning message box
            messagebox.Message(
                master=self,
                title='Error',
                icon='error',
                message="The region intended for cropping is out of the image boundaries. Please adjust the cropping area.\n\nYou can also right-click inside the ROI selection rectangle to remove it."
            ).show()
            # focus on window after clicking "OK" on the message box
            self.focus_force()
            return

        roi_start_coord, roi_end_coord = self._transform_cutout_coordinates()
        # add transformed coordinates to the cutout storage
        self.crop_storage.get('cutout')['transformed_coords'] = (roi_start_coord, roi_end_coord)
        # keep the cutout information in the display manager storage as well
        if self.crop_storage.key_exists('cutout'):
            self.display_manager.store(last_cutout=self.crop_storage.get('cutout'), force_update=True)
        # process the ROI image
        self.display_manager.process_roi_image_from_cropping(
            roi_coords = (roi_start_coord, roi_end_coord)
        )
        self.annotation_manager.register_annotation_proceedings()
        self.annotation_manager.clear_annotation_set()
        self.analysis_manager.clear_analysis()
        self.coordinator.reset_all_counting_stats()
        self.action_manager.clear_out_action_queue()
        self.state_manager.set_roi_as_cropped_from_source()
        self.state_manager.set_roi_as_assigned()
        self.layout_manager.disable_button_transfer_to_annotations()
        self.layout_manager.hide_button_toggle_auto_analysis()
        self.layout_manager.hide_button_save_auto_analysis()
        self.layout_manager.hide_button_toggle_annotations()
        self.layout_manager.hide_button_toggle_filter_output()
        self.layout_manager.show_tooling_panels()
        self.layout_manager.show_filter_options_panel()
        self.layout_manager.show_report_panel()
        self.layout_manager.show_auto_analysis_profile_panel()
        self.layout_manager.focus_on_auto_analysis_tab()

        self.destroy()
        self.display_manager.get_source_holder().display_image(self.display_manager.get_source_image())
        # print(self.display_manager.get_last_cropping())


    def _on_click(self, event):
        center, start, end = self._calculate_cutout_coordinates(event)
        # print(f"center: {center}, start: {start}, end: {end}")
        # print(f"crop size: {self._calculate_crop_size()}")
        # create a rectangle on the canvas if crop storage is empty (no rectangle exists on the canvas yet)
        if not self.crop_storage.key_exists('cutout'):
            self.crop_storage.add(
                cutout = {
                    'center': center,
                    'start':  start,
                    'end':    end,
                    'rectangle': self.image_holder.get_image_canvas().create_rectangle(
                        start[0], start[1], end[0], end[1],
                        outline = "limegreen",
                        width = self.crop_border_size,
                        # dash = (10, 10),
                    ),
                    'transformed_coords': None,
                }
            )
            # bind ux interaction events
            self._bind_interaction_events(event)
        else: # rectangle already exists; drag the existing rectangle to the new position
            self._update_cutout_coordinates(start, end, center)


    def _on_right_click(self, event):
        if self._cropping_ROI_exists():
            # only if right click is performed inside the rectangle
            if self.crop_storage.get('cutout')['start'][0] < event.x < self.crop_storage.get('cutout')['end'][0] and \
                self.crop_storage.get('cutout')['start'][1] < event.y < self.crop_storage.get('cutout')['end'][1]:
                # remove the rectangle from the canvas
                self.image_holder.get_image_canvas().delete(self.crop_storage.get('cutout')['rectangle'])
                self.crop_storage.remove('cutout')
                # unbind arrow key events
                self._unbind_arrow_keys()
                # unbind cutout keys
                self._unbind_cutout_keys()
                # unbind middle & right mouse click events
                self._unbind_middle_right_click()
                # unbind drag event
                self.image_holder.get_image_canvas().unbind("<B1-Motion")


    def _on_drag(self, event):
        center, start, end = self._calculate_cutout_coordinates(event)
        self._update_cutout_coordinates(start, end, center)


    def _get_cutout_coordinates(self):
        start = self.crop_storage.get('cutout')['start']
        end = self.crop_storage.get('cutout')['end']
        center = self.crop_storage.get('cutout')['center']
        return start, end, center


    def _get_resized_image_coordinates(self):
        canvas_width = self.image_holder.get_canvas_dimensions()[0] # type: ignore
        canvas_height = self.image_holder.get_canvas_dimensions()[1] # type: ignore
        resized_image_width = self.image_holder.get_image_entity().get_dimensions_resized()[0] # type: ignore
        resized_image_height = self.image_holder.get_image_entity().get_dimensions_resized()[1] # type: ignore

        top_left_x = (canvas_width - resized_image_width) // 2
        top_left_y = (canvas_height - resized_image_height) // 2
        bottom_right_x = top_left_x + resized_image_width
        bottom_right_y = top_left_y + resized_image_height

        return (top_left_x, top_left_y), (bottom_right_x, bottom_right_y)


    def _move_rectangle(self, direction):
        start, end, center = self._get_cutout_coordinates()
        if direction == 'left':
            center = (center[0]-1, center[1])
            start = (start[0]-1, start[1])
            end = (end[0]-1, end[1])
        elif direction == 'right':
            center = (center[0]+1, center[1])
            start = (start[0]+1, start[1])
            end = (end[0]+1, end[1])
        elif direction == 'up':
            center = (center[0], center[1]-1)
            start = (start[0], start[1]-1)
            end = (end[0], end[1]-1)
        elif direction == 'down':
            center = (center[0], center[1]+1)
            start = (start[0], start[1]+1)
            end = (end[0], end[1]+1)
        self._update_cutout_coordinates(start, end, center)


    def _calculate_cutout_coordinates(self, event):
        center_x, center_y = event.x, event.y
        crop_size_x, crop_size_y = self.crop_size
        crop_half_x, crop_half_y = crop_size_x//2, crop_size_y//2
        x0, y0 = center_x-crop_half_x, center_y-crop_half_y
        x1, y1 = center_x+crop_half_x, center_y+crop_half_y
        return (center_x, center_y), (x0, y0), (x1, y1)


    def _update_cutout_coordinates(self, start, end, center):
        if self.crop_storage.key_exists('cutout'):
            self.crop_storage.get('cutout')['start'] = start
            self.crop_storage.get('cutout')['end'] = end
            self.crop_storage.get('cutout')['center'] = center
            self.image_holder.get_image_canvas().coords(
                self.crop_storage.get('cutout')['rectangle'],
                start[0], start[1], end[0], end[1]
            )
            self.image_holder.get_image_canvas().update()
        # print(
        #     f"image dimensions: {self.image_holder.get_image_dimensions()} \n\
        #     canvas dimensions: {self.image_holder.get_canvas_dimensions()} \n\
        #     image resized dimensions: {self.image_holder.get_image_entity().get_dimensions_resized()} \n\
        #     resized coords: {self._get_resized_image_coordinates()} \n\
        #     start: {self.crop_storage.get('cutout')['start']}, end: {self.crop_storage.get('cutout')['end']} \n\
        #     transf_ coords: {self._transform_cutout_coordinates()} \n\
        #     resize ratio: {self.image_holder.get_image_entity().get_resize_ratio()} \n\
        # ")


    def _transform_cutout_coordinates(self):
        """
        Calculates the coordinates of the cropping rectangle on the original source image.
        This is done by transforming the coordinates of the cropping rectangle (displayed on resized version of the image on the canvas).
        """
        cutout_start, cutout_end, _ = self._get_cutout_coordinates()
        resized_img_top_left, resized_img_bottom_right = self._get_resized_image_coordinates()
        resize_ratio_x, resize_ratio_y = self.image_holder.get_image_entity().get_resize_ratio() # type: ignore
        x0 = int(round((cutout_start[0] - resized_img_top_left[0]) / resize_ratio_x))
        y0 = int(round((cutout_start[1] - resized_img_top_left[1]) / resize_ratio_y))
        # x1 = int(round((cutout_end[0] - resized_img_top_left[0]) / resize_ratio_x))
        # y1 = int(round((cutout_end[1] - resized_img_top_left[1]) / resize_ratio_y))
        # x1 = int(round(((cutout_end[0] - resized_img_top_left[0]) + 1) / resize_ratio_x) -1)
        # y1 = int(round(((cutout_end[1] - resized_img_top_left[1]) + 1) / resize_ratio_y) -1)
        roi_size_x, roi_size_y = self.roi_size
        x1 = x0 + roi_size_x
        y1 = y0 + roi_size_y
        return (x0, y0), (x1, y1)
