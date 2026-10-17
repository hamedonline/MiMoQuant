from managers.Manager import Manager


class StateManager(Manager):
    __slots__ = [
        'roi_is_cut_from_source',
        'roi_is_loaded_directly_from_file',
        'roi_is_assigned',
        'wsi_is_assigned',
        'auto_analysis_is_performed',
        'auto_analysis_img_is_on_display',
        'manual_analysis_img_is_on_display',
        'annotations_on_display',
    ]

    # ************************************************
    def __init__(self):
        self.roi_is_cut_from_source: bool = False
        self.roi_is_loaded_directly_from_file: bool = False
        self.roi_is_assigned: bool = False
        self.wsi_is_assigned: bool = False
        self.auto_analysis_img_is_on_display: bool = False
        self.manual_analysis_img_is_on_display: bool = False
        self.annotations_on_display: bool = False


    # ************************************************
    def set_roi_as_cropped_from_source(self):
        self.roi_is_cut_from_source = True
        self.unset_roi_as_loaded_from_file()

    def set_roi_as_loaded_from_file(self):
        self.roi_is_loaded_directly_from_file = True
        self.unset_roi_as_cropped_from_source()

    def unset_roi_as_cropped_from_source(self):
        self.roi_is_cut_from_source = False

    def unset_roi_as_loaded_from_file(self):
        self.roi_is_loaded_directly_from_file = False

    # ************************************************
    def set_roi_as_assigned(self):
        self.roi_is_assigned = True

    def set_wsi_as_assigned(self):
        self.wsi_is_assigned = True

    def unset_roi_as_assigned(self):
        self.roi_is_assigned = False

    def unset_wsi_as_assigned(self):
        self.wsi_is_assigned = False


    # ************************************************
    def set_auto_analysis_as_performed(self):
        self.auto_analysis_is_performed = True

    def set_auto_analysis_img_on_display(self):
        self.auto_analysis_img_is_on_display = True

    def set_manual_analysis_img_on_display(self):
        self.manual_analysis_img_is_on_display = True

    def set_annotations_on_display(self):
        self.annotations_on_display = True

    def unset_auto_analysis_as_performed(self):
        self.auto_analysis_is_performed = False

    def unset_auto_analysis_img_from_display(self):
        self.auto_analysis_img_is_on_display = False

    def unset_manual_analysis_img_from_display(self):
        self.manual_analysis_img_is_on_display = False

    def unset_annotations_from_display(self):
        self.annotations_on_display = False

    def unset_all_images_from_display(self):
        self.auto_analysis_img_is_on_display = False
        self.manual_analysis_img_is_on_display = False
        self.annotations_on_display = False


    # ************************************************
    def is_roi_from_source(self):
        return self.roi_is_cut_from_source

    def is_roi_from_file(self):
        return self.roi_is_loaded_directly_from_file

    def is_roi_assigned(self):
        return self.roi_is_assigned

    def is_wsi_assigned(self):
        return self.wsi_is_assigned

    def is_auto_analysis_performed(self):
        return self.auto_analysis_is_performed

    def is_auto_analysis_img_on_display(self):
        return self.auto_analysis_img_is_on_display

    def is_manual_analysis_img_on_display(self):
        return self.manual_analysis_img_is_on_display

    def is_annotations_on_display(self):
        return self.annotations_on_display
