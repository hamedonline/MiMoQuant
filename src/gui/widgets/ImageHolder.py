import tkinter as tk
import customtkinter as ctk
import traceback
from tkinter import ttk, filedialog
from CTkToolTip import CTkToolTip

from gui.widgets.Buttons import CloseButton2, ToggleButton, SaveButton
from utils.entities.canvas_entity import CanvasEntity
from utils.entities.image_entity import ImageEntity
from utils.entities.execution_queue import ExecutionQueue
from typing import Literal



class ImageHolder(ttk.Frame):
    def __init__(
        self, parent,
        canvas_args: dict = {},
        color_mode: Literal["rgb", "grayscale"] = "grayscale",
        has_close_button: bool = True,
        has_open_button: bool = True,
        has_toggle_button: bool = False,
        has_save_button: bool = False,
        open_button_label: str = "Load Image",
        open_button_size: tuple[int, int] = (140, 28),
        toggle_button_tooltip: str = "Toggle",
        load_command: ExecutionQueue | None = None,
        unload_command: ExecutionQueue | None = None,
        toggle_command: ExecutionQueue | None = None,
        save_command: ExecutionQueue | None = None,
        *args, **kwargs
    ):
        super().__init__(master=parent, *args, **kwargs)
        self.parent = parent
        self.rowconfigure((0,1), weight=1)
        self.columnconfigure(0, weight=1)

        self.has_open_button = has_open_button
        self.has_close_button = has_close_button
        self.has_toggle_button = has_toggle_button
        self.has_save_button = has_save_button
        self.canvas_args = canvas_args
        self.image_entity = ImageEntity.create_blank(color_mode=color_mode)
        self.load_command, self.unload_command, self.toggle_command, self.save_command, self.color_mode = load_command, unload_command, toggle_command, save_command, color_mode
        self.toggle_button_tooltip = toggle_button_tooltip
        self.toggle_btn_execution_trigger = self.toggle_command.execute_all if self.toggle_command is not None else None
        self.save_btn_execution_trigger = self.save_command.execute_all if self.save_command is not None else None
        self._apply_canvas_proceedings(**self.canvas_args)

        # spacer
        self.spacer = ttk.Label(master=self, text="", background="#dbdbdb")
        
        if has_open_button:
            if "dimension" in canvas_args.keys():
                width, height = canvas_args.get("dimension") # type: ignore
                padding_x = (width - open_button_size[0]) // 2
                padding_y = (height - open_button_size[1]) // 2
            else:
                padding_x = padding_y = 0
            self.button_holder = tk.Frame(
                master = self,
                padx = padding_x,
                pady = padding_y,
                bg = "#dbdbdb",
            )
            self.button_holder.grid(row=1, column=0)
            self.open_button = ctk.CTkButton(
                master=self.button_holder,
                text=open_button_label,
                cursor="hand2",
                command=self.open_image_dialog,
                fg_color="#3f5051",
                hover_color="#0F805A",
                text_color="white",
            )
            self.open_button.grid(row=0, column=0, sticky="nswe")


    def _show_spacer(self):
        self.spacer.grid(row=0, column=0)

    def _hide_spacer(self):
        self.spacer.grid_remove()


    def _generate_blank_canvas(self, **canvas_args):
        return CanvasEntity(master=self, **canvas_args)


    def _assign_canvas_buttons(self):
        if self.has_close_button:
            self.close_button = CloseButton2(
                parent=self.image_canvas.canvas,
                command=self.close_image,
            )
            self.close_button.place(relx=0.985, rely=0.015, anchor="ne")
            CTkToolTip(widget=self.close_button, message="Close", delay=0.5)

        if self.has_toggle_button:
            self.toggle_button = ToggleButton(
                parent=self.image_canvas.canvas,
                command=self.toggle_btn_execution_trigger,
            )
            self.toggle_button.place(relx=0.985, rely=0.98, anchor="se")
            CTkToolTip(widget=self.toggle_button, message=self.toggle_button_tooltip, delay=0.5)

        if self.has_save_button:
            self.save_button = SaveButton(
                parent=self.image_canvas.canvas,
                command=self.save_btn_execution_trigger,
            )
            self.save_button.place(relx=0.015, rely=0.98, anchor="sw")
            CTkToolTip(widget=self.save_button, message="Save Processed Image", delay=0.5)


    def _apply_canvas_proceedings(self, **canvas_args):
        self.image_canvas = self._generate_blank_canvas(**canvas_args)
        self._assign_canvas_buttons()


    def has_image_entity(self) -> bool:
        return (self.image_entity is not None) and (self.image_entity.has_image_array())


    def get_image_entity(self) -> ImageEntity:
        return self.image_entity


    def get_image_array(self):
        return self.image_entity.get_image_array()


    def get_image_canvas(self):
        return self.image_canvas.get_canvas()


    def get_canvas_padding_size(self):
        return self.image_canvas.get_padding_size()


    def get_image_dimensions(self):
        return self.image_entity.get_dimensions()


    def get_canvas_dimensions(self):
        return self.image_canvas.get_dimensions()


    def get_canvas_postscript(self):
        return self.image_canvas.get_postscript()


    def get_image_name(self):
        return self.image_entity.get_file_name()


    def get_image_file_info(self):
        return self.image_entity.get_file_info()


    # def add_load_command(self, *commands: tuple[Callable, tuple, dict, Optional[int]]):
    #     if self.load_command is None:
    #         self.load_command = ExecutionQueue()
    #     self.load_command.add_functions(*commands)


    def open_image_dialog(self):
        try:
            file_path = filedialog.askopenfilename(
                initialdir="",
                title="Select an image...",
                filetypes=(
                    ("All Supported Image Files", [
                        "*.bmp", "*.jpg", "*.jpeg", "*.jpe", "*.jp2", "*.png", "*.tif", "*.tiff",
                        "*.BMP", "*.JPG", "*.JPEG", "*.JPE", "*.JP2", "*.PNG", "*.TIF", "*.TIFF",
                    ]),
                    ("BMP", ["*.bmp", "*.BMP"]),
                    ("JPG", ["*.jpg", "*.jpeg", "*.jpe", "*.jp2",
                             "*.JPG", "*.JPEG", "*.JPE", "*.JP2"]),
                    ("PNG", ["*.png", "*.PNG"]),
                    ("TIFF", ["*.tif", "*.tiff", "*.TIF", "*.TIFF"]),
                )
            )

            if len(file_path) > 0:
                # self.image_canvas.close_canvas()
                if self.has_image_entity():
                    self.close_image()
                self.image_entity.import_from_file(file_path=file_path)
                self.image_canvas.draw_image(self.image_entity)

                self.hide_load_button()
                self._hide_spacer()

                if self.load_command is not None:
                    print("Running load commands...")
                    self.load_command.execute_all()

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error loading image: {e}",
                  f"Error details:\n{error_details}", sep="\n"
            )


    def register_load_command(self, command: ExecutionQueue):
        self.load_command = command


    def register_unload_command(self, command: ExecutionQueue):
        self.unload_command = command


    def display_image(self, image: ImageEntity):
        self._hide_spacer()
        self.image_entity = image
        self.image_canvas.draw_image(self.image_entity)


    def close_image(self):
        self.clear()
        if self.unload_command is not None:
            print("Running unload commands...")
            self.unload_command.execute_all()
        self._show_spacer()
        if self.has_open_button:
            self.reveal_open_button()


    def clear(self):
        self.image_entity.clear_out()
        self.image_canvas.close_canvas()


    def reveal_open_button(self):
        if self.has_open_button:
            # self.open_button.grid(row=0, column=0, sticky="nswe")
            self.button_holder.grid(row=0, column=0)

    def hide_load_button(self):
        if self.has_open_button:
            # self.open_button.grid_remove()
            self.button_holder.grid_remove()

    def reveal_toggle_button(self):
        if self.has_toggle_button and not self.toggle_button.winfo_viewable():
            self.toggle_button.place(relx=0.985, rely=0.98, anchor="se")

    def hide_toggle_button(self):
        if self.has_toggle_button:
            self.toggle_button.place_forget()

    def reveal_save_button(self):
        if self.has_save_button and not self.save_button.winfo_viewable():
            self.save_button.place(relx=0.015, rely=0.98, anchor="sw")

    def hide_save_button(self):
        if self.has_save_button:
            self.save_button.place_forget()
