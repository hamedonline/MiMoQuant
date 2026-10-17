import tkinter as tk
import customtkinter as ctk



class ValueSlider(ctk.CTkFrame):
    def __init__(
            self, 
            parent, 
            label: str,
            value_range: tuple[int, int] | tuple[float, float], 
            step_precision: int | float,
            # default_value: int | float | None = None,
            value_object: tk.IntVar | ctk.IntVar | tk.DoubleVar | ctk.DoubleVar,
            width: int = 145,
            *args, **kwargs
        ):
        super().__init__(master=parent, *args, **kwargs)

        self.value_object = value_object
        self.text_color = "#fff"
        self.entry_text_color = "#3f5051"
        self.slider_color = "#a1a1a1"
        self.button_color = "#20e9a8"
        self.button_hover_color = "#15ba85"

        # define grid structure
        # self.columnconfigure((0,1,2), weight=(1,5,1))
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.rowconfigure((0,1), weight=1)

        # calculate step value based on provided range and step_precision
        self.range_min, self.range_max = value_range
        self.step_precision = step_precision
        self.num_steps = (self.range_max - self.range_min) / self.step_precision
        self.to_number = float if isinstance(self.step_precision, float) else int

        # create widgets

        ######### CTK WIDGETS #########
        # empty label for padding (to align stacked sliders with decimal values better)
        self.empty_label = ctk.CTkLabel(self, text="", text_color=self.text_color)
        self.empty_label.grid(row=0, column=0, sticky="e", padx=16)

        # label for the widget
        self.label = ctk.CTkLabel(self, text=label, text_color=self.text_color)
        self.label.grid(row=0, column=1, sticky="w", padx=5)

        # an entry field for the current value of the slider
        self.entry_value = ctk.CTkEntry(self, width=45, text_color=self.entry_text_color)
        self.entry_value.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.entry_value.bind("<Return>", self.update_via_entry)
        self.entry_value.bind("<FocusOut>", self.update_via_entry)

        # slider
        self.slider = ctk.CTkSlider(
            self, from_=self.range_min, to=self.range_max, number_of_steps=int(self.num_steps), # type: ignore
            fg_color=self.slider_color, button_color=self.button_color, button_hover_color=self.button_hover_color,
            orientation='horizontal', command=self.update_via_slider,
            width=width,
        )
        self.slider.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        # if default_value is not None:
        #     self.slider.set(default_value)
        self.slider.set(self.value_object.get())
        self.update_via_slider(self.slider.get())

        # labels for the minimum and maximum values of the slider
        self.min_label = ctk.CTkLabel(self, text=str(self.range_min), text_color=self.text_color)
        self.min_label.grid(row=1, column=0, sticky="e", padx=5)

        self.max_label = ctk.CTkLabel(self, text=str(self.range_max), text_color=self.text_color)
        self.max_label.grid(row=1, column=2, sticky="w", padx=5)
        #############################



        # ######### TK WIDGETS #########
        # # label for the widget
        # self.label = tk.Label(self, text=label)
        # self.label.grid(row=0, column=0, sticky="w")

        # # an entry field for the current value of the slider
        # self.entry_value = tk.Entry(self, width=5)
        # self.entry_value.grid(row=0, column=2, sticky="w")
        # self.entry_value.bind("<Return>", self.sync_slider)

        # # slider
        # self.slider = tk.Scale(self, from_=range_min, to=range_max, bigincrement=num_steps,
        #                             orient='horizontal', command=self.update_entry)
        # self.slider.grid(row=1, column=1, sticky="ew")
        ## if default_value is not None:
        ##     self.slider.set(default_value)
        # self.slider.set(self.value_object.get())

        # # Create labels for the minimum and maximum values of the slider
        # self.min_label = tk.Label(self, text=str(range_min))
        # self.min_label.grid(row=1, column=0, sticky="e")

        # self.max_label = tk.Label(self, text=str(range_max))
        # self.max_label.grid(row=1, column=2, sticky="w")
        # #############################


    def count_decimal_digits(self, num: float | int) -> int:
        """
        Returns the count of digits after the decimal point for a given number.
        """
        if not isinstance(num, (int, float)):
            raise TypeError('The input must be either an integer or a float number.')
        return 0 if isinstance(num, int) else len(str(num).split('.')[-1])


    def cast_value_change(self, value):
        self.value_object.set(value)
        # print(self.value_object.get())


    def modify_entry_field(self, new_val):
        value = round(new_val, self.count_decimal_digits(self.step_precision)) if self.to_number is float else self.to_number(new_val)
        self.entry_value.delete(0, "end")
        self.entry_value.insert(0, value)


    def update_via_entry(self, event=None):
        value = self.entry_value.get() # get value from the entry field (it is in string format)
        value = self.to_number(float(value)) if value.replace('.', '', 1).isdigit() else self.to_number(self.range_min)
        value = round(value, self.count_decimal_digits(self.step_precision))
        self.slider.set(value)
        self.cast_value_change(self.slider.get())
        self.modify_entry_field(self.slider.get()) # update entry value again to cover edge-cases


    def update_via_slider(self, new_val):
        value = self.to_number(new_val)
        self.cast_value_change(value)
        self.modify_entry_field(value) # update the entry field with the new value


    def update_via_tracing(self, *args):
        value = self.value_object.get()
        self.slider.set(value)
        self.modify_entry_field(value)