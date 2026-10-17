import tkinter as tk
from tkinter import ttk
from managers.Coordinator import Coordinator



class BottomFrame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, coordinator: Coordinator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.coordinator = coordinator

        self.style = ttk.Style(self)
        self.style.configure(
            "bottom_frame.TFrame",
            # background="grey"
        )
        self.configure(style="bottom_frame.TFrame")

        # define grid for the bottom frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure([0,1,2], weight=1)

        self.create_widgets()


    def create_widgets(self):
        ttk.Separator(master=self,orient=tk.HORIZONTAL).grid(row=1, column=0, sticky="ew")

        self.writing_label = ttk.Label(
            master = self,
            text=self.coordinator.retrieve('version_info'),
            font=("Arial", 8),
            justify="center",
            foreground="#3f5051",
            # background="yellow",
            # textvariable = self.storage.retrieve('version_info'),
        ).grid(row=2, column=0)
