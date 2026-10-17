import customtkinter as ctk



class Panel(ctk.CTkFrame):
    """
    A Panel class that extends CTkFrame to create a grid of rows and columns with specified weights.

    Args:
        parent (CTkFrame): The parent frame.
        num_rows (int, optional): The number of rows in the grid. Defaults to 1.
        num_cols (int, optional): The number of columns in the grid. Defaults to 1.
        row_weights (list[int], optional): A list of weights for the rows. Defaults to None.
        col_weights (list[int], optional): A list of weights for the columns. Defaults to None.

    Raises:
        ValueError: If the number of row weights does not match num_rows or the number of column weights does not match num_cols.

    Example:
        panel = Panel(parent, num_rows=2, num_cols=2, row_weights=[1, 2], col_weights=[2, 1])
    """

    def __init__(self, parent, num_rows=1, num_cols=1, row_weights=None, col_weights=None, *args, **kwargs):
        super().__init__(master=parent, *args, **kwargs)

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
