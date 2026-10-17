from tkinter import ttk


class TopFrame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.style = ttk.Style(self)
        self.style.configure("top_frame.TFrame", background="green")
        self.configure(style="top_frame.TFrame")

        # define grid for the top frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # self.create_widgets()


    def create_widgets(self):
        ttk.Label(
            master=self,
            text="Top Frame",
            font=("Arial", 16),
            justify="center",
            foreground="grey"
        ).grid()

        ttk.Label(
            master=self,
            text="Topw22 Frame",
            font=("Arial", 12),
            justify="center",
            foreground="blue"
        ).grid()
