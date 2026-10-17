import tkinter as tk
from tkinter import ttk
from typing import Callable



class LabelInput(ttk.Frame):
    """
    A compound widget for a label and input box combined together.
    """

    def __init__(
            self,
            parent: tk.Frame | ttk.Frame,
            label: str,
            input_class: Callable,
            label_args: dict = {},
            input_args: dict = {},
            layout_orientation: str = "horizontal", # or "vertical"
            *args, **kwargs
        ):
        super().__init__(parent, *args, **kwargs)

        if layout_orientation not in ["horizontal", "vertical"]:
            raise ValueError("Invalid layout orientation. Must be 'horizontal' or 'vertical'.")

        self.label = ttk.Label(self, text=label)
        self.label.configure(**label_args)

        self.input = input_class(self)
        self.input.configure(**input_args)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        if layout_orientation == "horizontal":
            self.label.grid(column=0, row=0, sticky="w", padx=2, pady=5)
            self.input.grid(column=1, row=0, sticky="e", padx=2, pady=5)
        else: # vertical
            self.label.grid(column=0, row=0, sticky="w", columnspan=2, padx=5, pady=2)
            self.input.grid(column=0, row=1, sticky="w", columnspan=2, padx=5, pady=2)
