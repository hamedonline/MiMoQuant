import tkinter as tk

from managers.Coordinator import Coordinator
from gui.layout.MainWindow import MainWindow
from gui.layout.LayoutFrameMainWindow import LayoutFrameMainWindow
from gui.layout.ContentFrame import ContentFrame
# from gui.layout.TopFrame import TopFrame
from gui.layout.LeftFrame import LeftFrame
from gui.layout.RightFrame import RightFrame
from gui.layout.BottomFrame import BottomFrame

import sys
if getattr(sys, 'frozen', False):
    import pyi_splash  # type: ignore



class GUIApp():
    __slots__ = [
        'coordinator',
        'display_manager',
        'layout_manager',
        'main_window',
        'layout_frame',
        'content_frame',
        'left_frame',
        'right_frame',
        'bottom_frame',
    ]


    def __init__(self, coordinator: Coordinator) -> None:
        self.coordinator = coordinator
        self.display_manager = self.coordinator.ask_for_manager('display')
        self.layout_manager = self.coordinator.ask_for_manager('layout')


    def initialize_layout(self):
        self.main_window = MainWindow(
            coordinator = self.coordinator,
            window_title = self.coordinator.retrieve('window_title_main'),
            window_size_ratio = self.coordinator.retrieve('window_size_ratio'),
            window_geometry = self.coordinator.retrieve('window_geometry'),
            app_icon_path = self.coordinator.retrieve('icon_path'),
        )
        self.assign_post_main_window_variables()

        self.layout_frame = LayoutFrameMainWindow(
            parent=self.main_window,
        )
        self.layout_frame.grid(sticky="nsew")

        # self.top_frame = TopFrame(
        #     parent=self.layout_frame,
        # )
        # self.top_frame.grid(column=0, row=0, columnspan=3, sticky="nsew")

        self.left_frame = LeftFrame(
            parent = self.layout_frame,
            coordinator = self.coordinator,
        )
        self.left_frame.grid(column=0, row=1, sticky="nsew")

        self.right_frame = RightFrame(
            parent = self.layout_frame,
            coordinator = self.coordinator,
        )
        self.right_frame.grid(column=2, row=1, sticky="nsew")

        self.content_frame = ContentFrame(
            parent = self.layout_frame,
            coordinator = self.coordinator,
            canvas_size = self.display_manager.get_canvas_size()
        )
        self.content_frame.grid(column=1, row=1, sticky="nsew")

        self.bottom_frame = BottomFrame(
            parent = self.layout_frame,
            coordinator = self.coordinator,
        )
        self.bottom_frame.grid(column=0, row=2, columnspan=3, sticky="nsew")

        self.layout_manager.store(
            data_dict = {
                'windows': {
                    'main_window': self.main_window
                },
                'frames': {
                    'layout_frame': self.layout_frame,
                    # 'top_frame': self.top_frame,
                    'left_frame': self.left_frame,
                    'right_frame': self.right_frame,
                    'content_frame': self.content_frame,
                    'bottom_frame': self.bottom_frame,
                }
            }
        )


    def assign_post_main_window_variables(self):
        self.coordinator.store(
            data_dict={
                'count_stats': {
                    'auto': {
                        'dots': tk.IntVar(value=0),
                        'branches': tk.IntVar(value=0)
                    },
                    'annotated': {
                        'dots': tk.IntVar(value=0),
                        'branches': tk.IntVar(value=0),
                    }
                },
                'annotation_type': tk.IntVar(value=0),
                'roi_size': {
                    'width': tk.IntVar(value=self.coordinator.retrieve('initial_cutout_size')[0]),
                    'height': tk.IntVar(value=self.coordinator.retrieve('initial_cutout_size')[1])
                },
                'conf_thresholds': {
                    'dots': tk.DoubleVar(value=self.coordinator.retrieve('initial_conf_thresh_dots')),
                    'branches': tk.DoubleVar(value=self.coordinator.retrieve('initial_conf_thresh_branches'))
                }
            }
        )

    def confirm_bootloader_run(self):
        return getattr(sys, 'frozen', False)

    def trigger_app(self):
        self.main_window.mainloop()

    def run(self):
        if self.confirm_bootloader_run():
            pyi_splash.update_text('Initializing app UI...')

        self.initialize_layout()
        for manager in self.coordinator.retrieve('managers').values():
            manager.perform_post_init_tasks()

        self.display_manager.set_main_window(self.main_window)
        if self.confirm_bootloader_run():
            pyi_splash.close()
        self.trigger_app()
