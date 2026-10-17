from managers.Manager import Manager



class LayoutManager(Manager):
    def __init__(self, **kwargs):
        super().__init__()


# ************************************************
    def get_widget_source_holder(self):
        return self.retrieve('frames').get('left_frame').source_holder

    def get_widget_roi_holder(self):
        return self.retrieve('frames').get('content_frame').roi_holder

    def get_widget_annotation_holder(self):
        return self.retrieve('frames').get('content_frame').annotation_holder

    def get_widget_manual_analysis_holder(self):
        return self.retrieve('frames').get('content_frame').manual_analysis_holder


    # ************************************************
    def focus_on_auto_analysis_tab(self):
        self.retrieve('frames').get('content_frame').roi_sections_tab.set('Auto-Analysis')

    def focus_on_filter_output_tab(self):
        self.retrieve('frames').get('content_frame').roi_sections_tab.set('Filter-Output')

    def focus_on_annotation_tab(self):
        self.retrieve('frames').get('content_frame').roi_sections_tab.set('Annotation')


    # ************************************************
    def show_panel_auto_analysis(self):
        self.retrieve('frames').get('content_frame').auto_analysis_tools_panel.grid()

    def hide_panel_auto_analysis(self):
        self.retrieve('frames').get('content_frame').auto_analysis_tools_panel.grid_remove()

    def show_panel_manual_analysis(self):
        self.retrieve('frames').get('content_frame').manual_analysis_tools_panel.grid()

    def hide_panel_manual_analysis(self):
        self.retrieve('frames').get('content_frame').manual_analysis_tools_panel.grid_remove()

    def show_panel_annotation(self):
        self.retrieve('frames').get('content_frame').annotation_tools_panel.grid()

    def hide_panel_annotation(self):
        self.retrieve('frames').get('content_frame').annotation_tools_panel.grid_remove()

    def show_tooling_panels(self):
        self.show_panel_auto_analysis()
        self.show_panel_manual_analysis()
        self.show_panel_annotation()

    def hide_tooling_panels(self):
        self.hide_panel_auto_analysis()
        self.hide_panel_manual_analysis()
        self.hide_panel_annotation()

    def show_filter_options_panel(self):
        self.retrieve('frames').get('right_frame').filter_options_tab.grid()

    def hide_filter_options_panel(self):
        self.retrieve('frames').get('right_frame').filter_options_tab.grid_remove()

    def show_auto_analysis_options_panel(self):
        self.retrieve('frames').get('right_frame').auto_analysis_options_tab.grid()

    def hide_auto_analysis_options_panel(self):
        self.retrieve('frames').get('right_frame').auto_analysis_options_tab.grid_remove()

    def show_auto_analysis_profile_panel(self):
        self.retrieve('frames').get('left_frame').analysis_profile_tab.grid()

    def hide_auto_analysis_profile_panel(self):
        self.retrieve('frames').get('left_frame').analysis_profile_tab.grid_remove()

    def show_report_panel(self):
        self.retrieve('frames').get('left_frame').report_tab.grid()

    def hide_report_panel(self):
        self.retrieve('frames').get('left_frame').report_tab.grid_remove()


    # ************************************************
    def enable_button_transfer_to_annotations(self):
        self.retrieve('frames').get('content_frame').transform_to_annotations_button.configure(state="normal")

    def disable_button_transfer_to_annotations(self):
        self.retrieve('frames').get('content_frame').transform_to_annotations_button.configure(state="disabled")


    # ************************************************
    def show_button_toggle_auto_analysis(self):
        self.get_widget_roi_holder().reveal_toggle_button()

    def hide_button_toggle_auto_analysis(self):
        self.get_widget_roi_holder().hide_toggle_button()

    def show_button_save_auto_analysis(self):
        self.get_widget_roi_holder().reveal_save_button()

    def hide_button_save_auto_analysis(self):
        self.get_widget_roi_holder().hide_save_button()

    def show_button_toggle_annotations(self):
        self.get_widget_annotation_holder().reveal_toggle_button()

    def hide_button_toggle_annotations(self):
        self.get_widget_annotation_holder().hide_toggle_button()

    def show_button_toggle_filter_output(self):
        self.get_widget_manual_analysis_holder().reveal_toggle_button()

    def hide_button_toggle_filter_output(self):
        self.get_widget_manual_analysis_holder().hide_toggle_button()
