import tkinter as tk
# import customtkinter
from gui.layout.MenuBar import MenuBar
from managers.Coordinator import Coordinator


class MainWindow(tk.Tk):
    __slots__ = [
        'coordinator',
        'display_manager',
        'app_width',
        'app_height',
        'menu_bar'
    ]

    def __init__(
        self,
        coordinator: Coordinator,
        window_title: str,
        window_size_ratio: tuple[float, float] | None,
        window_geometry: str | None,
        app_icon_path: str | None = None,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.coordinator = coordinator
        self.display_manager = self.coordinator.ask_for_manager('display')

        # # Configure Tkinter scaling to match system DPI (required for DPI-aware apps)
        # if self.coordinator.os_is_windows():
        #     self._configure_dpi_scaling()

        # main window setup
        if window_size_ratio is None and window_geometry is None:
            raise ValueError("At least one of window_size_ratio or window_geometry must be provided.")
        if (window_size_ratio is not None):
            screen_width, screen_height = self.display_manager.get_screen_resolution()
            self.app_width = int(screen_width * window_size_ratio[0])
            self.app_height = int(screen_height * window_size_ratio[1])
            center_x = int(screen_width/2 - self.app_width/2)
            center_y = int(screen_height/2 - self.app_height/2)
            self.geometry(f'{self.app_width}x{self.app_height}+{center_x}+{center_y}')
        elif window_geometry is not None:
            self.app_width, self.app_height = self.display_manager.get_screen_resolution()
            self.geometry(window_geometry)

        self.title(window_title)
        if app_icon_path is not None:
            icon = tk.PhotoImage(file=app_icon_path)
            self.iconphoto(False, icon)
        self.minsize(self.app_width, self.app_height)
        self._maximize_window()
        self.resizable(True, True)
        self.deiconify()

        self.menu_bar = MenuBar(self, self.coordinator)

        # grid setup
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # self.grid()


    def _maximize_window(self):
        """
        Maximize the window across platforms with fallbacks.

        - Windows: `state('zoomed')` is typically supported.
        - Linux: many WMs use `attributes('-zoomed', True)`.
        - Fallback: force fullscreen-sized geometry.
        """
        try:
            self.state('zoomed')
            return
        except tk.TclError:
            pass

        try:
            self.attributes('-zoomed', True)
            return
        except tk.TclError:
            pass

        screen_width, screen_height = self.display_manager.get_screen_resolution()
        self.geometry(f"{screen_width}x{screen_height}+0+0")


    def _configure_dpi_scaling(self):
        """
        Configure Tkinter's internal scaling to match the actual system DPI.
        
        When DPI awareness is enabled via SetProcessDpiAwareness(1), Windows 
        reports physical pixels, but Tkinter's internal scaling remains at its
        default value (typically assuming 96 DPI). This mismatch causes canvas
        and other widgets to render at incorrect sizes on scaled displays.
        
        This method synchronizes Tkinter's scaling factor with the system DPI.
        """
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
            # Get the actual system DPI (96 is baseline = 100% scaling)
            actual_dpi = windll.user32.GetDpiForSystem()
            # Calculate the scaling factor (96 DPI = 1.0)
            scaling_factor = actual_dpi / 96.0
            # Set Tkinter's scaling to match
            self.tk.call('tk', 'scaling', scaling_factor)
            print(f"System DPI: {actual_dpi}, Tk scaling set to: {scaling_factor}")
        except Exception as e:
            print(f"Warning: Could not configure DPI scaling: {e}")
