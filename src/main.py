from gui.GUIApp import GUIApp
from managers.Coordinator import Coordinator
from managers.StateManager import StateManager
from managers.LayoutManager import LayoutManager
from managers.ActionManager import ActionManager
from managers.DisplayManager import DisplayManager
from managers.AnnotationManager import AnnotationManager
from managers.AnalysisManager import AnalysisManager
from managers.FileManager import FileManager
from managers.ReportManager import ReportManager



if __name__ == "__main__":

    coordinator = Coordinator()
    coordinator.store(
        data_dict={
            "app": {
                "icon_path": "./assets/app_icon.png",
                "version_info": "version: 0.3.1"
            },
            "ui": {
                "main_window": {
                    "window_title_main": "MiMoQuant - Mitochondria Morphology Quantification Tool",
                    "window_size_ratio": (0.95, 0.9),  # ratio that is used to calculate minimum width and height of the app window with respect to the current screen size
                    "window_geometry": "1280x720+0+0",  # only if the above ratio is zero, the following geometry is considered for the minimum window size (format: widthxheight+x+y)
                    "label_of_the_puncts": "Puncta",
                    "label_of_the_branchings": "Branchings",
                    "ann_size_factor": 1.0,  # used as the scale factor in calculating annotation objects size on ROI exports
                    "base_canvas_size_as_metric": 600,  # in pixels, used for the calculation of the scale factor in determining the size of annotation objects on canvas
                },
                "cutout_window": {
                    "window_title_cutout": "ROI Selection...",
                    "initial_cutout_size": (300, 300),  # width, height in pixels: this is initial size in case no previously config file exists
                },
            },
            "global_vars": {
                "annotation_metadata_file_extension": "hmd",
            },
            "analysis": {
                "confidence_threshold": {
                    "initial_conf_thresh_dots": 0.25,
                    "initial_conf_thresh_branches": 0.15,
                }
            },
            "images": {
                "roi": None,
                "source": None,
                "auto_processed": None,
                "manually_processed": None,
                "annotation": None,
            },
            "holders": {
                "roi": None,
                "source": None,
                "manual_analysis": None,
                "annotation": None,
            },
        }
    )

    state_manager = StateManager()
    layout_manager = LayoutManager()
    file_manager = FileManager(coordinator)
    annotation_manager = AnnotationManager(coordinator)
    display_manager = DisplayManager(coordinator)
    action_manager = ActionManager(coordinator)
    analysis_manager = AnalysisManager(coordinator)
    report_manager = ReportManager(coordinator)

    coordinator.store(
        data_dict={
            "managers": {
                "state": state_manager,
                "layout": layout_manager,
                "file": file_manager,
                "display": display_manager,
                "action": action_manager,
                "annotation": annotation_manager,
                "analysis": analysis_manager,
                "report": report_manager,
            },
        }
    )

    app = GUIApp(
        coordinator=coordinator,
    )
    app.run()
