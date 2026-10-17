from tkinter import messagebox
from managers.Manager import Manager
from managers.Coordinator import Coordinator
from utils.image.general import expand_channel
from utils.entities.image_entity import ImageEntity
from analyzers.ClassificationInfo import ClassificationInfo
from analyzers.yolox.engine import YOLOXEngine
from analyzers.yolox.parameters import InferenceSettings



class AnalysisManager(Manager):
    __slots__ = [
        'coordinator',
        'display_manager',
        'state_manager',
        'layout_manager',
        'annotation_manager',
        'classification_info',
        'inference_settings',
        'analysis_engine',
    ]

    # ************************************************
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__()
        self.coordinator = coordinator

    def assign_comanagers(self):
        self.display_manager = self.coordinator.ask_for_manager('display')
        self.state_manager = self.coordinator.ask_for_manager('state')
        self.layout_manager = self.coordinator.ask_for_manager('layout')
        self.annotation_manager = self.coordinator.ask_for_manager('annotation')

    def perform_post_init_tasks(self):
        self.assign_comanagers()
        self.assign_essentials()


    def assign_essentials(self):
        class_names = {
            "Punct": 0,
            "Branching": 1
        }

        # threshold level definitions
        threshold_levels = {
            "low": 0.2,
            "medium": 0.4,
            "high": 0.6
        }

        # color profiles for each class based on threshold levels
        color_profiles = {
            "Punct": {
                "low": (255, 180, 180),  # light red
                "medium": (255, 120, 120),  # medium red
                "high": (255, 0, 0),  # red
            },
            "Branching": {
                "low": (180, 255, 180),  # light green
                "medium": (120, 255, 120),  # medium green
                "high": (0, 255, 0),  # green
            }
        }

        self.classification_info = ClassificationInfo(
            label_to_index=class_names,
            color_profiles=color_profiles,
            threshold_levels=threshold_levels
        )

        self.inference_settings = [
            InferenceSettings(
                class_id=0,  # Puncta
                model_path='./analyzers/yolox/models/medium_260224_299.onnx',
                input_shape=(320, 320),
                conf_threshold=self.coordinator.get_var_conf_threshold_dots(),
                nms_threshold=0.4
            ),
            InferenceSettings(
                class_id=1,  # Branching
                model_path='./analyzers/yolox/models/medium_260224_299.onnx',
                input_shape=(320, 320),
                conf_threshold=self.coordinator.get_var_conf_threshold_branches(),
                nms_threshold=0.4
            )
        ]

        self.analysis_engine = YOLOXEngine(
            classification_info=self.classification_info,
            inference_settings=self.inference_settings
        )


    # ************************************************
    def check_and_update_confidence_threshold(self, *args):
        conf_value_dots_input = self.coordinator.get_var_conf_threshold_dots()
        conf_value_dots_engine = self.analysis_engine.get_conf_threshold(class_id=0)
        conf_value_branches_input = self.coordinator.get_var_conf_threshold_branches()
        conf_value_branches_engine = self.analysis_engine.get_conf_threshold(class_id=1)
        if conf_value_dots_input != conf_value_dots_engine:
            self.analysis_engine.update_conf_threshold(class_id=0, new_conf_threshold=conf_value_dots_input)
        if conf_value_branches_input != conf_value_branches_engine:
            self.analysis_engine.update_conf_threshold(class_id=1, new_conf_threshold=conf_value_branches_input)


    # ************************************************
    def perform_analysis(self):
        if self.display_manager.roi_image_exists():
            input_image = self.display_manager.get_roi_image().get_np_image()
            input_image = expand_channel(input_image)
            self.analysis_engine.perform(image_array=input_image)
            results = self.analysis_engine.get_results()

            num_results_all = len(results.get('unified').get('bboxes'))
            num_results_dots = len(results.get('class_specific').get(0).get('bboxes'))
            num_results_branches = len(results.get('class_specific').get(1).get('bboxes'))
            if num_results_all == 0:
                messagebox.showinfo(
                    title = "Auto-Analysis",
                    message = "No objectives were detected in selected region."
                )
                return

            visualized_image_array = self.analysis_engine.visualize_results(
                image_array=input_image,
            )
            auto_analysis_img = ImageEntity(
                image_array=visualized_image_array,
                color_mode='grayscale'
            )

            self.display_manager.unset_auto_processed_image()
            self.display_manager.set_auto_processed_image(auto_analysis_img)
            self.display_manager.get_roi_holder().display_image(self.display_manager.get_auto_processed_image()) # type: ignore
            self.layout_manager.show_button_toggle_auto_analysis()
            self.layout_manager.show_button_save_auto_analysis()
            self.layout_manager.focus_on_auto_analysis_tab()
            self.state_manager.set_auto_analysis_img_on_display()

            print("Auto-Analysis performed.")

            # store the detected blobs
            self.store(
                data_dict={
                    'recognized_dots': results.get('class_specific').get(0).get('bboxes'),
                    'recognized_branches': results.get('class_specific').get(1).get('bboxes'),
                },
                force_update=True
            )
            # update stats
            self.coordinator.retrieve('count_stats').get('auto').get('dots').set(num_results_dots) # type: ignore
            self.coordinator.retrieve('count_stats').get('auto').get('branches').set(num_results_branches) # type: ignore

            # enable "Transfer to Annotation" button
            self.layout_manager.enable_button_transfer_to_annotations()


    def clear_analysis(self):
        if self.has_key('recognized_dots'):
            self.remove('recognized_dots')
        if self.has_key('recognized_branches'):
            self.remove('recognized_branches')


    def transform_to_annotations(self):
        self.annotation_manager.import_from_analysis_dots(self.retrieve('recognized_dots'))
        self.annotation_manager.import_from_analysis_branches(self.retrieve('recognized_branches'))
        # self.layout_manager.disable_button_transfer_to_annotations()
        self.layout_manager.focus_on_annotation_tab()
