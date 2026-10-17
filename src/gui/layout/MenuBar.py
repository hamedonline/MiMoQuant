import tkinter as tk
from tkinter import messagebox
from managers.Coordinator import Coordinator
from managers.ReportManager import ReportManager



class MenuBar(tk.Menu):
    __slots__ = [
        'parent',
        'coordinator',
        'layout_manager',
        'display_manager',
        'file_manager',
        'file_menu',
        'tools_menu',
    ]

    def __init__(
        self,
        parent: tk.Tk,
        coordinator: Coordinator,
        *args, **kwargs
    ) -> None:

        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.coordinator = coordinator
        self.layout_manager = self.coordinator.ask_for_manager('layout')
        self.display_manager = self.coordinator.ask_for_manager('display')
        self.file_manager = self.coordinator.ask_for_manager('file')
        self.report_manager = self.coordinator.ask_for_manager('report')

        self.file_menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label="Open WSI Image", command=self.open_wsi_dialog)
        self.file_menu.add_command(label="Open ROI Image", command=self.open_roi_dialog)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_app)
        self.add_cascade(label="File", menu=self.file_menu)

        self.tools_menu = tk.Menu(self, tearoff=0)
        self.tools_menu.add_command(label="Generate Report File", command=self.initiate_report_generation)
        self.add_cascade(label="Tools", menu=self.tools_menu)

        parent.config(menu=self)


    def open_wsi_dialog(self):
        self.display_manager.open_wsi_load_dialog()

    def open_roi_dialog(self):
        self.display_manager.open_roi_load_dialog()

    def initiate_report_generation(self):
        dir_path = self.file_manager.select_directory_via_dialog(
            window_title = "Select the root directory to look for annotations..."
        )
        if dir_path is not None and len(dir_path) > 0:
            annotation_report_df = self.report_manager.generate_spreadsheet_df(dir_path)
            if len(annotation_report_df) > 0:
                saved_file_path = self.file_manager.save_excel_via_dialog(
                    data_frame = annotation_report_df,
                    window_title = "Save the report file as...",
                    file_name = ReportManager.generate_unique_annotations_report_filename(),
                    sheet_name = ReportManager.get_annotations_report_filename(),
                )
                if saved_file_path is not None and len(saved_file_path) > 0:
                    # tkinter message box with option to open the file
                    response = messagebox.askyesno(
                        "Report File Generated Successfully",
                        f"Report saved to:\n{saved_file_path}\n\nWould you like to open the file now?"
                    )
                    if response:
                        self.file_manager.launch_from_path(saved_file_path)

    def exit_app(self):
        self.parent.destroy()
