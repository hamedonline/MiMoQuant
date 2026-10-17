import customtkinter as ctk


class TabsFrame(ctk.CTkTabview):
    def __init__(self, parent, tab_names: list[str], num_rows=1, num_cols=1, row_weights=None, col_weights=None, * args, **kwargs):
        super().__init__(master=parent, *args, **kwargs)
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)

        self.tab_names = tab_names
        for tab_name in self.tab_names:
            self.add(tab_name)

        row_weights = row_weights or [1] * num_rows
        col_weights = col_weights or [1] * num_cols

        if len(row_weights) != num_rows:
            raise ValueError(
                f"Number of items for row weights ({len(row_weights)}) does not match num_rows ({num_rows})")
        if len(col_weights) != num_cols:
            raise ValueError(
                f"Number of items for column weights ({len(col_weights)}) does not match num_cols ({num_cols})")

        for i in range(num_rows):
            self.rowconfigure(i, weight=row_weights[i])
        for i in range(num_cols):
            self.columnconfigure(i, weight=col_weights[i])
