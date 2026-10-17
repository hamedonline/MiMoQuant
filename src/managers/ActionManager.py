from managers.Coordinator import Coordinator
from utils.entities.image_entity import ImageEntity



class ActionManager:
    __slots__ = [
        'coordinator',
        'display_manager',
        'state_manager',
        'layout_manager',
        'image_storage',
        'holder_storage',
        'action_queue',
    ]

    # ************************************************
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__()
        self.coordinator = coordinator
        self.image_storage = self.coordinator.retrieve('images')
        self.holder_storage = self.coordinator.retrieve('holders')
        self.action_queue = []

    def assign_comanagers(self):
        self.display_manager = self.coordinator.ask_for_manager('display')
        self.state_manager = self.coordinator.ask_for_manager('state')
        self.layout_manager = self.coordinator.ask_for_manager('layout')

    def perform_post_init_tasks(self):
        self.assign_comanagers()


    # ************************************************
    def action_queue_is_empty(self):
        return len(self.action_queue) == 0

    def clear_out_action_queue(self):
        if not self.action_queue_is_empty():
            for action in self.action_queue:
                action.disable()
            self.action_queue.clear()

    def sort_action_queue_by_priority(self):
        if not self.action_queue_is_empty():
            self.action_queue.sort(key=lambda x: x.get_priority(), reverse=True)

    def add_action(self, action):
        if action not in self.action_queue:
            self.action_queue.append(action)
            self.sort_action_queue_by_priority()

    def remove_action(self, action):
        if action in self.action_queue:
            self.action_queue.remove(action)
            self.sort_action_queue_by_priority()

    def _update_toggle_button_visibility(self):
        if not self.action_queue_is_empty():
            self.layout_manager.show_button_toggle_filter_output()
        else:
            self.layout_manager.hide_button_toggle_filter_output()

    def inform_action_update(self, *args):
        print("Action queue updated.")
        self.execute_action_queue()
        self._update_toggle_button_visibility()

    def execute_action_queue(self):
        if (self.display_manager.manually_processed_image_exists()) and (not self.action_queue_is_empty()):
            # trigger action chain execution on the source image
            image_entity = ImageEntity(
                image_array=self.display_manager.get_roi_image().get_np_image(),
                color_mode='grayscale',
            )
            for action in self.action_queue:
                image_entity = action.execute(image_entity)

            # update processed image with the result of chain actions on the ROI image
            self.display_manager.set_manually_processed_image(image_entity)
            # redraw the ROI canvas with the updated processed image
            self.display_manager.get_manual_analysis_holder().display_image(self.display_manager.get_manually_processed_image()) # type: ignore
            self.state_manager.set_manual_analysis_img_on_display()
            self.layout_manager.focus_on_filter_output_tab()
            # ugly hack: force-toggle auto-analysis to display the auto-processed image
            # this is to ensure roi image doesn't get disappeared on auto-analysis holder when it is also displayed on this holder
            self.state_manager.unset_auto_analysis_img_from_display()
            self.display_manager.toggle_image_auto_analysis()

        else:
            # if there are no actions to execute, just redraw the ROI canvas with the ROI image
            print("No actions to execute.")
            if self.display_manager.roi_image_exists():
                self.display_manager.get_manual_analysis_holder().display_image(self.display_manager.get_roi_image()) # type: ignore
                self.state_manager.unset_manual_analysis_img_from_display()
                # ugly hack: force-toggle auto-analysis to display the auto-processed image
                # this is to ensure roi image doesn't get disappeared on auto-analysis holder when it is also displayed on this holder
                self.state_manager.unset_auto_analysis_img_from_display()
                self.display_manager.toggle_image_auto_analysis()
