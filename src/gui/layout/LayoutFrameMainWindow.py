import tkinter as tk
from tkinter import ttk


class LayoutFrameMainWindow(ttk.Frame):
    def __init__(self, parent: tk.Tk, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.img_canvas = tk.Canvas(self, bg="cyan")
        # storage_handler.add(img_canvas=self.img_canvas)
        

        # define grid for the layout frame
        self.columnconfigure(0, weight=3, uniform="layout columns")
        self.columnconfigure(1, weight=6, uniform="layout columns")
        self.columnconfigure(2, weight=3, uniform="layout columns")
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=23)
        self.rowconfigure(2, weight=1)
