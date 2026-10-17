import tkinter as tk
import customtkinter as ctk



class CloseButton(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(master=parent, *args, **kwargs)
        self.configure(text="X")
        self.place(relx=0.99, rely=0.01, anchor="ne")


class CloseButton2(ctk.CTkButton):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(master=parent, *args, **kwargs)
        self.configure(
            width=18,
            height=25,
            bg_color="red",
            fg_color="red",
            hover_color="crimson",
            cursor="hand2",
            text="❌",
            text_color="white",
            font=("Arial", 12, )
        )


class ToggleButton(ctk.CTkButton):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(master=parent, *args, **kwargs)
        self.configure(
            width=16,
            height=32,
            bg_color="#5e8ac6",
            fg_color="#5e8ac6",
            hover_color="#00a8ec",
            cursor="hand2",
            text="🔁",
            text_color="white",
            font=("Arial", 24, )
        )


class SaveButton(ctk.CTkButton):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(master=parent, *args, **kwargs)
        self.configure(
            width=16,
            height=32,
            bg_color="#5e8ac6",
            fg_color="#5e8ac6",
            hover_color="#00a8ec",
            cursor="hand2",
            text="💾",
            text_color="white",
            font=("Arial", 24, )
        )
