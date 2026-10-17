from typing import Any, Literal
from tkinter import messagebox, Tk
from managers.Manager import Manager
from managers.Coordinator import Coordinator
from utils.entities.image_entity import ImageEntity
from gui.widgets.ImageHolder import ImageHolder



class DisplayManager(Manager):
    __slots__ = [
        'coordinator',
        'state_manager',
        'annotation_manager',
        'action_manager',
        'layout_manager',
        'image_storage',
        'holder_storage',
        'main_window',

        'screen_resolution',
        'suitable_canvas_size',
    ]


    # ************************************************
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__()
        self.coordinator = coordinator
        self.image_storage = self.coordinator.retrieve('images')
        self.holder_storage = self.coordinator.retrieve('holders')
        # self.store(data_dict={'last_cutout': dict()})
        self.screen_resolution: tuple[int, int] = self.extract_screen_dimensions()
        self.suitable_canvas_size: tuple[int, int] = self.determine_canvas_size(self.screen_resolution)

    def assign_comanagers(self):
        self.state_manager = self.coordinator.ask_for_manager('state')
        self.annotation_manager = self.coordinator.ask_for_manager('annotation')
        self.action_manager = self.coordinator.ask_for_manager('action')
        self.layout_manager = self.coordinator.ask_for_manager('layout')

    def perform_post_init_tasks(self):
        self.assign_comanagers()


    # ************************************************
    def set_main_window(self, main_window):
        self.main_window = main_window

    def refresh_main_window(self):
        self.main_window.deiconify()
        print("Main window refreshed.")

    def push_info_message(
        self,
        parent: Any | None,
        title: str,
        message: str,
        message_type: Literal["info", "warning", "error", "question"] = "info",
    ) -> None:
        messagebox.Message(
            master = parent,
            title = title,
            icon = message_type,
            message = message
        ).show()
        if parent is not None:
            # focus on window after clicking "OK" on the message box
            parent.focus_force()

    @staticmethod
    def extract_curr_screen_geometry():
        """
        Workaround to get the size of the current screen (even in a multi-screen setups).

        Returns:
            str: The geometry string of the current screen, in the following format:
                "[width]x[height]+[left]+[top]"
        """
        root = Tk()
        root.update_idletasks()
        root.attributes('-fullscreen', True)
        root.state('iconic')

        # # the following might fail in multi-screen setups
        # width, height = root.winfo_screenwidth(), root.winfo_screenheight()
        # root.destroy()
        # return (width, height)

        geometry = root.winfo_geometry()
        root.destroy()
        return geometry

    @staticmethod
    def parse_screen_geometry(geo_string: str) -> tuple[int, int, int, int]:
        """
        Parses geometry numbers from a given geometry string and returns it as a list of integers.
        The geometry is expected to be in the format "WxH+X+Y" or "WxH-X-Y" which is the format used by the geometry option of the Tkinter geometry method.
        W is the width, H is the height, X is the x position and Y is the y position. This function retains the sign of the x and y positions.

        Args:
            geo_string (str): the string to extract the geometry specifications from

        Returns:
            tuple[int]: the geometry as a list of integers in the following order: [width, height, x, y]
        """
        separators = ["x", "+", "-"]

        numbers = []
        current = ""
        sign = 1

        for char in geo_string:
            # if the character is a digit, append it to the current number
            if char.isdigit():
                current += char
            # if the character is one of the separators, add the current number to the list and reset it
            elif char in separators:
                if current:
                    numbers.append(sign * int(current))
                    current = ""
                # update the sign based on the separator
                if char == "+":
                    sign = 1
                elif char == "-":
                    sign = -1
        # add the last number to the list if any
        if current:
            numbers.append(sign * int(current))
        return tuple(numbers)

    @staticmethod
    def extract_screen_dimensions() -> tuple[int, int]:
        """
        Get the dimensions of the current screen.

        Returns:
            tuple[int, int]: A tuple containing the width and height of the screen.
        """
        screen_geometry = DisplayManager.extract_curr_screen_geometry()
        screen_dimension: tuple[int, int] = DisplayManager.parse_screen_geometry(screen_geometry)[:2]
        return screen_dimension

    @staticmethod
    def determine_canvas_size(screen_resolution: tuple[int, int]) -> tuple[int, int]:
        """
        Determine the optimal canvas size based on screen resolution's aspect ratio and height.

        Args:
            screen_resolution (tuple): (screen_width, screen_height) in pixels

        Returns:
            tuple: (canvas_width, canvas_height) in pixels

        Raises:
            ValueError: For invalid input dimensions
        """
        # Constants configuration
        STANDARD_ASPECT_RATIOS = {
            '16:9': 16/9,
            '16:10': 16/10,
            '4:3': 4/3,
            '21:9': 21/9,
            '1:1': 1,
        }

        CANVAS_SIZES = {
            '16:9': [
                (2160, (1550, 1550)), # (3840, 2160)
                (1440, (1050, 1050)), # (2560, 1440)
                (1080, (775, 775)),   # (1920, 1080)
                (900,  (625, 625)),   # (1600, 900)
                (864,  (600, 600)),   # (1536, 864)
                (768,  (475, 475)),   # (1366, 768)
                (720,  (425, 425)),   # (1280, 720)
            ],
            '16:10': [
                (1200, (825, 825)), # (1920, 1200)
                (1050, (725, 725)), # (1680, 1050)
                (960,  (650, 650)), # (1536, 960)
                (900,  (600, 600)), # (1440, 900)
                (840,  (525, 525)), # (1344, 840)
                (800,  (500, 500)), # (1280, 800)
                (640,  (400, 400)), # (1024, 640)
            ],
            '4:3': [
                (1200, (825, 825)), # (1600, 1200)
                (1080, (675, 675)), # (1440, 1080)
                (1050, (675, 675)), # (1400, 1050)
                (900,  (575, 575)), # (1200, 900)
                (864,  (550, 550)), # (1152, 864)
                (768,  (475, 475)), # (1024, 768)
                (720,  (450, 450)), # (960, 720)
                (600,  (350, 350)), # (800, 600)
            ],
            '21:9': [
                (1600, (1120, 1120)), # (3840, 1600)   *****
                (1440, (1050, 1050)), # (3440, 1440)
                (1080, (775, 775)), # (2560, 1080)
                (864,  (600, 600)), # (2048, 864)
                (720,  (450, 450)), # (1707, 720)

            ],
            '1:1': [
                (1080, (500)), # (1080, 1080)
                (720,  (320)), # (720, 720)
            ],
        }

        ASPECT_RATIO_TOLERANCE = 0.1
        DEFAULT_ASPECT_RATIO = '16:9'
        DEFAULT_CANVAS_SIZE = (600, 600)

        # input validation
        try:
            screen_width, screen_height = screen_resolution
        except (TypeError, ValueError):
            raise ValueError("Invalid screen resolution format. Expected tuple (width, height).")

        if screen_width <= 0 or screen_height <= 0:
            raise ValueError("Screen resolution dimensions must be positive integers.")

        # calculate screen aspect ratio
        try:
            screen_ratio = screen_width / screen_height
        except ZeroDivisionError:
            raise ValueError("Screen height cannot be zero.")

        # find closest standard aspect ratio
        closest_aspect = None
        min_diff = float('inf')
        for aspect_name, target_ratio in STANDARD_ASPECT_RATIOS.items():
            diff = abs(screen_ratio - target_ratio)
            if diff < min_diff:
                min_diff = diff
                closest_aspect = aspect_name

        # apply tolerance threshold
        if min_diff > ASPECT_RATIO_TOLERANCE:
            closest_aspect = DEFAULT_ASPECT_RATIO

        # get and sort canvas options for the aspect ratio, defaulting to empty list if aspect not found
        aspect_options = CANVAS_SIZES.get(closest_aspect or DEFAULT_ASPECT_RATIO, [])
        canvas_options = sorted(aspect_options, key=lambda x: x[0], reverse=True)

        if not canvas_options:
            return DEFAULT_CANVAS_SIZE

        # find appropriate canvas size
        for height_threshold, canvas_size in canvas_options:
            if screen_height >= height_threshold:
                # print(f"Screen resolution {screen_resolution} matched with {closest_aspect}, selected canvas size: {canvas_size}")
                return canvas_size

        # fallback to smallest available size for the aspect ratio
        return canvas_options[-1][1]


    # ************************************************
    def get_screen_resolution(self):
        return self.screen_resolution

    def get_canvas_size(self):
        return self.suitable_canvas_size


    # ************************************************
    def get_source_holder(self) -> ImageHolder | None:
        return self.holder_storage.get('source')

    def get_roi_holder(self) -> ImageHolder | None:
        return self.holder_storage.get('roi')

    def get_manual_analysis_holder(self) -> ImageHolder | None:
        return self.holder_storage.get('manual_analysis')

    def get_annotation_holder(self) -> ImageHolder | None:
        return self.holder_storage.get('annotation')


    # ************************************************
    def open_roi_load_dialog(self):
        roi_holder = self.get_roi_holder()
        if roi_holder is not None:
            roi_holder.open_image_dialog()

    def open_wsi_load_dialog(self):
        source_holder = self.get_source_holder()
        if source_holder is not None:
            source_holder.open_image_dialog()


    # ************************************************
    def get_source_image(self) -> ImageEntity | None:
        return self.image_storage.get('source')

    def get_roi_image(self) -> ImageEntity | None:
        return self.image_storage.get('roi')

    def get_auto_processed_image(self) -> ImageEntity | None:
        return self.image_storage.get('auto_processed')

    def get_manually_processed_image(self) -> ImageEntity | None:
        return self.image_storage.get('manually_processed')

    def get_annotation_image(self) -> ImageEntity | None:
        return self.image_storage.get('annotation')


    # ************************************************
    def source_image_exists(self):
        return self.get_source_image() is not None

    def roi_image_exists(self):
        return self.get_roi_image() is not None

    def auto_processed_image_exists(self):
        return self.get_auto_processed_image() is not None

    def manually_processed_image_exists(self):
        return self.get_manually_processed_image() is not None

    def annotation_image_exists(self):
        return self.get_annotation_image() is not None


    # ************************************************
    def source_holder_exists(self):
        return self.get_source_holder() is not None

    def roi_holder_exists(self):
        return self.get_roi_holder() is not None

    def manual_analysis_holder_exists(self):
        return self.get_manual_analysis_holder() is not None

    def annotation_holder_exists(self):
        return self.get_annotation_holder() is not None


    # ************************************************
    def set_source_image(self, image_entity: ImageEntity):
        self.image_storage.update(source=image_entity)
        print("Source image set.")

    def set_roi_image(self, image_entity: ImageEntity):
        self.image_storage.update(roi=image_entity)
        print("ROI image set.")

    def set_auto_processed_image(self, image_entity: ImageEntity):
        self.image_storage.update(auto_processed=image_entity)
        print("Auto-process image set.")

    def set_manually_processed_image(self, image_entity: ImageEntity):
        self.image_storage.update(manually_processed=image_entity)
        print("Manual-process image set.")

    def set_annotation_image(self, image_entity: ImageEntity):
        self.image_storage.update(annotation=image_entity)
        print("Annotation image set.")


    # ************************************************
    def unset_source_image(self):
        if self.source_image_exists():
            self.image_storage.update(source=None)
            print("Source image unset.")

    def unset_roi_image(self):
        if self.roi_image_exists():
            self.image_storage.update(roi=None)
            print("ROI image unset.")

    def unset_auto_processed_image(self):
        if self.auto_processed_image_exists():
            self.image_storage.update(auto_processed=None)
            print("Auto-process image unset.")

    def unset_manually_processed_image(self):
        if self.manually_processed_image_exists():
            self.image_storage.update(manually_processed=None)
            print("Manual-process image unset.")

    def unset_annotation_image(self):
        if self.annotation_image_exists():
            self.image_storage.update(annotation=None)
            print("Annotation image unset.")


    # ************************************************
    def unset_source_holder(self):
        if self.source_holder_exists():
            self.holder_storage.update(source=None)
            print("Source holder unset.")

    def unset_roi_holder(self):
        if self.roi_holder_exists():
            self.holder_storage.update(roi=None)
            print("ROI holder unset.")

    def unset_manual_analysis_holder(self):
        if self.manual_analysis_holder_exists():
            self.holder_storage.update(manual_analysis=None)
            print("Manual-analysis holder unset.")

    def unset_annotation_holder(self):
        if self.annotation_holder_exists():
            self.holder_storage.update(annotation=None)
            print("Annotation holder unset.")


    # ************************************************
    def register_source_holder(self, source_holder: ImageHolder):
        # source_holder.get_image_canvas().configure(cursor="dotbox")
        self.holder_storage.update(source = source_holder)
        # self.set_source_image(source_holder.get_image_entity()) # type: ignore

    def register_roi_holder(self, roi_holder: ImageHolder):
        self.holder_storage.update(roi = roi_holder)

    def register_manual_analysis_holder(self, manual_analysis_holder: ImageHolder):
        self.holder_storage.update(manual_analysis = manual_analysis_holder)

    def register_annotation_holder(self, annotation_holder: ImageHolder):
        self.holder_storage.update(annotation = annotation_holder)


    # ************************************************
    def evacuate_roi_zone_images(self):
        self.unset_roi_image()
        self.unset_auto_processed_image()
        self.unset_manually_processed_image()
        self.unset_annotation_image()
        print("ROI zone images emptied.")

    def evacuate_source_image(self):
        self.unset_source_image()
        # clear last cutout data if it has been set already
        if self.storage.key_exists('last_cutout'):
            self.storage.remove('last_cutout')
        print("Source image emptied.")

    def evacuate_roi_zone_holders(self):
        self.unset_roi_holder()
        self.unset_manual_analysis_holder()
        self.unset_annotation_holder()
        print("ROI zone holders emptied.")

    def evacuate_source_holder(self):
        self.unset_source_holder()
        print("Source holder emptied.")

    def clear_other_holders(self):
        # self.get_manual_analysis_holder().clear() # type: ignore
        # self.get_annotation_holder().clear() # type: ignore
        self.get_manual_analysis_holder().close_image() # type: ignore
        self.get_annotation_holder().close_image() # type: ignore

    def prepare_and_set_roi_zone_images(self):
        # prepare the ROI zone images
        roi_img = ImageEntity(
            image_array=self.get_roi_holder().get_image_array(), # type: ignore
            color_mode='grayscale'
        )
        roi_img.set_file_path(self.get_roi_holder().get_image_entity().get_file_path()) # type: ignore
        auto_analysis_img = ImageEntity(
            image_array=self.get_roi_holder().get_image_array(), # type: ignore
            color_mode='grayscale'
        )
        manual_analysis_img = ImageEntity(
            image_array=self.get_roi_holder().get_image_array(),  # type: ignore
            color_mode='grayscale'
        )
        annotation_img = ImageEntity(
            image_array=self.get_roi_holder().get_image_array(),  # type: ignore
            color_mode='grayscale'
        )
        # clear the previously ROI zone images (garbage collection)
        self.evacuate_roi_zone_images()
        # set the new ROI zone images
        self.set_roi_image(roi_img)
        self.set_auto_processed_image(auto_analysis_img)
        self.set_manually_processed_image(manual_analysis_img)
        self.set_annotation_image(annotation_img)
        # put the new ROI zone images on display
        self.get_roi_holder().display_image(self.get_auto_processed_image()) # type: ignore
        self.state_manager.set_auto_analysis_img_on_display()
        self.get_manual_analysis_holder().display_image(self.get_manually_processed_image()) # type: ignore
        self.state_manager.set_manual_analysis_img_on_display()
        self.get_annotation_holder().display_image(self.get_annotation_image()) # type: ignore
        self.state_manager.set_annotations_on_display()
        print("ROI zone images prepared and set.")

    def prepare_and_set_source_image(self):
        # clear the previous source image (garbage collection)
        self.evacuate_source_image()
        # change the hover cursor to something more suitable for ROI selection
        self.get_source_holder().get_image_canvas().configure(cursor="dotbox") # type: ignore
        self.set_source_image(self.get_source_holder().get_image_entity()) # type: ignore

    def process_roi_image_from_cropping(self, roi_coords: tuple[tuple[int, int], tuple[int, int]]):
        roi_start_coord, roi_end_coord = roi_coords
        img_ROI_np = self.get_source_image().get_np_image()[roi_start_coord[1]:roi_end_coord[1], roi_start_coord[0]:roi_end_coord[0]] # type: ignore
        img_ROI_entity = ImageEntity.create_from_array(img_ROI_np)
        img_ROI_entity.set_file_path(self.get_source_image().get_file_path()) # type: ignore
        self.get_roi_holder().display_image(img_ROI_entity) # type: ignore
        self.get_roi_holder().hide_load_button() # type: ignore
        self.prepare_and_set_roi_zone_images()


    # ************************************************
    def get_last_cropping(self):
        return self.retrieve('last_cutout')

    def get_roi_coords(self):
        return self.get_last_cropping().get('transformed_coords', None)


    # ************************************************
    def toggle_image_auto_analysis(self):
        if (self.roi_image_exists()) and (self.auto_processed_image_exists()):
            if self.state_manager.is_auto_analysis_img_on_display():
                self.get_roi_holder().display_image(self.get_roi_image()) # type: ignore
                self.state_manager.unset_auto_analysis_img_from_display()
                self.layout_manager.hide_button_save_auto_analysis()
                # ugly hack: force-toggle manual-analysis to display the manually-processed image
                # this is to ensure roi image doesn't get disappeared on filter-output holder when it is also displayed on this holder
                self.state_manager.unset_manual_analysis_img_from_display()
                self.toggle_image_manual_analysis()
            else:
                self.get_roi_holder().display_image(self.get_auto_processed_image()) # type: ignore
                self.state_manager.set_auto_analysis_img_on_display()
                self.layout_manager.show_button_save_auto_analysis()
        # make sure annotations are active after every toggle act
        if not self.state_manager.is_annotations_on_display():
            self.toggle_image_annotation()

    def toggle_image_manual_analysis(self):
        if (self.roi_image_exists()) and (self.manually_processed_image_exists()) and (not self.action_manager.action_queue_is_empty()):
            if self.state_manager.is_manual_analysis_img_on_display():
                self.get_manual_analysis_holder().display_image(self.get_roi_image()) # type: ignore
                self.state_manager.unset_manual_analysis_img_from_display()
                # ugly hack: force-toggle auto-analysis to display the auto-processed image
                # this is to ensure roi image doesn't get disappeared on auto-analysis holder when it is also displayed on this holder
                self.state_manager.unset_auto_analysis_img_from_display()
                self.toggle_image_auto_analysis()
            else:
                self.get_manual_analysis_holder().display_image(self.get_manually_processed_image()) # type: ignore
                self.state_manager.set_manual_analysis_img_on_display()
        # make sure annotations are active after every toggle act
        if not self.state_manager.is_annotations_on_display():
            self.toggle_image_annotation()

    def toggle_image_annotation(self):
        if self.roi_image_exists() and self.annotation_manager.has_annotations():
            if self.state_manager.is_annotations_on_display():
                self.annotation_manager.hide_annotations()
                self.annotation_manager.unbind_annotation_keys()
                self.state_manager.unset_annotations_from_display()
            else:
                self.annotation_manager.show_annotations()
                self.annotation_manager.bind_annotation_keys()
                self.state_manager.set_annotations_on_display()
