from platform import system as platform_system
from managers.Manager import Manager



class Coordinator(Manager):
    __slots__ = [

    ]

    # ************************************************
    def __init__(self) -> None:
        super().__init__()

    def ask_for_manager(self, manager_name: str):
        managers = self.retrieve('managers') or {}
        manager_reference = managers.get(manager_name)
        if manager_reference is not None:
            return manager_reference
        else:
            raise ValueError(f"Manager with the name '{manager_name}' not found.")


# ************************************************
    def _get_os_name(self):
        return platform_system().lower()

    def os_is_windows(self):
        return True if self._get_os_name() == "windows" else False

    def os_is_linux(self):
        return True if self._get_os_name() == "linux" else False

    def os_is_mac(self):
        return True if self._get_os_name() == "darwin" else False


    # ************************************************
    def get_global_annotation_metadata_file_extension(self):
        return self.retrieve('annotation_metadata_file_extension')

    def get_global_label_of_the_puncts(self):
        return self.retrieve('label_of_the_puncts')

    def get_global_label_of_the_branchings(self):
        return self.retrieve('label_of_the_branchings')

    def get_global_ann_size_factor(self):
        return self.retrieve('ann_size_factor')

    def get_global_canvas_size_as_metric(self):
        return self.retrieve('base_canvas_size_as_metric')


    # ************************************************
    def get_var_initial_cutout_size(self):
        return self.retrieve('initial_cutout_size')

    def get_var_cutout_size(self):
        return (self.get_obj_roi_width().get(), self.get_obj_roi_height().get())

    def get_var_conf_threshold_dots(self):
        return self.get_obj_conf_threshold_dots().get()

    def get_var_conf_threshold_branches(self):
        return self.get_obj_conf_threshold_branches().get()

    def get_obj_roi_width(self):
        return self.retrieve('roi_size').get('width')

    def get_obj_roi_height(self):
        return self.retrieve('roi_size').get('height')

    def get_obj_conf_threshold_dots(self):
        return self.retrieve('conf_thresholds').get('dots')

    def get_obj_conf_threshold_branches(self):
        return self.retrieve('conf_thresholds').get('branches')

    def get_var_annotation_type(self):
        return self.retrieve('annotation_type')

    def get_var_counting_stats(self):
        return self.retrieve('count_stats')

    def get_var_annotations_count(self, annotation_type_id: int):
        count_stats = self.get_var_counting_stats()
        if count_stats:
            if annotation_type_id == 0:
                return count_stats.get('annotated').get('dots')
            elif annotation_type_id == 1:
                return count_stats.get('annotated').get('branches')
        else:
            raise ValueError("Count stats variable not found for the provided annotation type id.")

    def set_var_roi_width(self, value: int):
        variable_to_change = self.get_obj_roi_width()
        if variable_to_change:
            variable_to_change.set(value)

    def set_var_roi_height(self, value: int):
        variable_to_change = self.get_obj_roi_height()
        if variable_to_change:
            variable_to_change.set(value)

    def set_var_cutout_size(self, width: int, height: int):
        self.set_var_roi_width(width)
        self.set_var_roi_height(height)

    def set_var_conf_threshold_dots(self, value: float):
        variable_to_change = self.get_obj_conf_threshold_dots()
        if variable_to_change:
            variable_to_change.set(value)

    def set_var_conf_threshold_branches(self, value: float):
        variable_to_change = self.get_obj_conf_threshold_branches()
        if variable_to_change:
            variable_to_change.set(value)

    def set_var_annotations_count(self, annotation_type_id: int, value: int):
        variable_to_change = self.get_var_annotations_count(annotation_type_id)
        if variable_to_change:
            variable_to_change.set(value)

    def reset_var_conf_threshold_dots(self):
        self.set_var_conf_threshold_dots(self.retrieve('initial_conf_thresh_dots'))

    def reset_var_conf_threshold_branches(self):
        self.set_var_conf_threshold_branches(self.retrieve('initial_conf_thresh_branches'))

    def reset_annotation_stats(self):
        count_stats = self.get_var_counting_stats()
        if count_stats:
            count_stats.get('annotated').get('dots').set(0)
            count_stats.get('annotated').get('branches').set(0)

    def reset_auto_analysis_stats(self):
        count_stats = self.get_var_counting_stats()
        if count_stats:
            count_stats.get('auto').get('dots').set(0)
            count_stats.get('auto').get('branches').set(0)

    def reset_all_counting_stats(self):
        self.reset_annotation_stats()
        self.reset_auto_analysis_stats()
