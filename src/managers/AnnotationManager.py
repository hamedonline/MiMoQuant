# from numpy import array
from typing import Literal
from PIL import Image, ImageDraw, ImageFont
# from io import BytesIO
from tkinter import messagebox

from managers.Manager import Manager
from managers.Coordinator import Coordinator
from gui.annotation.AnnotationSet import AnnotationSet
from gui.annotation.AnnotationCircle import AnnotationCircle
from gui.annotation.AnnotationCrossMark import AnnotationCrossMark
from gui.annotation.AnnotationObjectInterface import AnnotationObjectInterface
from utils.image.general import expand_channel



class AnnotationManager(Manager):
    __slots__ = [
        'coordinator',
        'state_manager',
        'display_manager',
        'layout_manager',
        'file_manager',
        'color_circles',
        'color_crossmarks',
        'annotation_object_sizes',
        'annotation_file_extension',
    ]

    # ************************************************
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__()
        self.coordinator = coordinator
        self.color_circles = '#FF0000'
        self.color_crossmarks = '#00FF00'
        self.annotation_file_extension = self.coordinator.get_global_annotation_metadata_file_extension()

    def assign_comanagers(self):
        self.state_manager = self.coordinator.ask_for_manager('state')
        self.display_manager = self.coordinator.ask_for_manager('display')
        self.layout_manager = self.coordinator.ask_for_manager('layout')
        self.file_manager = self.coordinator.ask_for_manager('file')

    def perform_post_init_tasks(self):
        self.assign_comanagers()
        self.annotation_object_sizes = self._determine_annotation_object_sizes()


    # ************************************************
    def _determine_annotation_object_sizes(self):
        roi_size = self.coordinator.get_var_cutout_size()
        roi_longer_side_size = max(roi_size)
        roi_ann_scale_factor = self.coordinator.get_global_ann_size_factor()
        ann_circle_longer_side_size_on_roi = max(AnnotationCircle.get_default_size_on_roi())
        ann_crossmark_longer_side_size_on_roi = max(AnnotationCrossMark.get_default_size_on_roi())
        division_factor_for_circle_on_roi = (roi_longer_side_size / ann_circle_longer_side_size_on_roi) / roi_ann_scale_factor
        division_factor_for_crossmark_on_roi = (roi_longer_side_size / ann_crossmark_longer_side_size_on_roi) / roi_ann_scale_factor
        canvas_size = self.display_manager.get_canvas_size()
        canvas_longer_side_size = max(canvas_size)
        canvas_ann_scale_ratio = canvas_longer_side_size / self.coordinator.get_global_canvas_size_as_metric()
        ann_circle_longer_side_size_on_canvas = max(AnnotationCircle.get_default_size_on_canvas())
        ann_crossmark_longer_side_size_on_canvas = max(AnnotationCrossMark.get_default_size_on_canvas())
        division_factor_for_circle_on_canvas = (canvas_longer_side_size / ann_circle_longer_side_size_on_canvas) / canvas_ann_scale_ratio
        division_factor_for_crossmark_on_canvas = (canvas_longer_side_size / ann_crossmark_longer_side_size_on_canvas) / canvas_ann_scale_ratio
        annotation_object_sizes = {
            'roi': {
                AnnotationCircle.get_name_label(): (int(roi_longer_side_size // division_factor_for_circle_on_roi), int(roi_longer_side_size // division_factor_for_circle_on_roi)),
                AnnotationCrossMark.get_name_label(): (int(roi_longer_side_size // division_factor_for_crossmark_on_roi), int(roi_longer_side_size // division_factor_for_crossmark_on_roi))
            },
            'canvas': {
                AnnotationCircle.get_name_label(): (int(canvas_longer_side_size // division_factor_for_circle_on_canvas), int(canvas_longer_side_size // division_factor_for_circle_on_canvas)),
                AnnotationCrossMark.get_name_label(): (int(canvas_longer_side_size // division_factor_for_crossmark_on_canvas), int(canvas_longer_side_size // division_factor_for_crossmark_on_canvas))
            }
        }
        return annotation_object_sizes

    def _get_annotation_set(self):
        annotation_set = self.retrieve('annotation_set')
        if annotation_set is None:
            raise ValueError("No annotation set is initialized, you need to register the annotation set first.")
        return annotation_set

    def _get_annotation_objects(self, belonging_group_label: str | None = None):
        annotation_set = self._get_annotation_set()
        return annotation_set.get_objects(belonging_group_label)

    def get_suitable_object_sizes(self, on: Literal['roi', 'canvas']):
        return self.annotation_object_sizes.get(on, {})


    # ************************************************
    def bind_annotation_keys(self):
        self.display_manager.get_annotation_holder().get_image_canvas().bind("<Button-1>", self._on_roi_left_click)
        self.display_manager.get_annotation_holder().get_image_canvas().bind("<Button-3>", self._on_roi_right_click)
        self.display_manager.get_annotation_holder().get_image_canvas().configure(cursor="plus")

    def unbind_annotation_keys(self):
        self.display_manager.get_annotation_holder().get_image_canvas().unbind("<Button-1>")
        self.display_manager.get_annotation_holder().get_image_canvas().unbind("<Button-3>")
        self.display_manager.get_annotation_holder().get_image_canvas().configure(cursor="arrow")

    def register_annotation_proceedings(self):
        if not self.storage.key_exists('annotation_set'):
            # create a new annotation set for the ROI holder
            self.store(
                annotation_set = AnnotationSet(
                    parent_canvas = self.display_manager.get_annotation_holder().get_image_canvas() # type: ignore
                )
            )
        else:
            self.clear_annotation_set()
        self.bind_annotation_keys()


    # ************************************************

    def map_coordinate_points(self, canvas_coords: tuple[int, int], fix_pixels: tuple[int, int] = (0, 0)) -> tuple[int, int]:
        """
        Converts coordinates from canvas space to original image space.

        Args:
            canvas_coords: Tuple of (x,y) coordinates on the canvas
            fix_pixels: Optional tuple of (x,y) additional pixel adjustments

        Returns:
            Tuple of (x,y) coordinates on the original image
        """
        # get entity handlers
        annotation_holder = self.display_manager.get_annotation_holder()
        image_entity = annotation_holder.get_image_entity()

        # get scale ratios
        scale_ratio_width, scale_ratio_height = image_entity.get_resize_ratio()

        # get canvas padding (if any)
        canvas_padding_size = annotation_holder.get_canvas_padding_size()
        canvas_padding_x, canvas_padding_y = (canvas_padding_size, canvas_padding_size)

        # adjust for canvas padding
        adjusted_x = canvas_coords[0] - canvas_padding_x
        adjusted_y = canvas_coords[1] - canvas_padding_y

        # apply optional fix pixels
        adjusted_x += fix_pixels[0]
        adjusted_y += fix_pixels[1]

        # convert to original image coordinates
        original_x = int(round(adjusted_x / scale_ratio_width))
        original_y = int(round(adjusted_y / scale_ratio_height))

        # ensure coordinates are within image bounds
        original_width, original_height = image_entity.get_dimensions()
        original_x = max(0, min(original_x, original_width - 1))
        original_y = max(0, min(original_y, original_height - 1))

        return (original_x, original_y)


    # ************************************************
    def hide_annotations(self):
        for object_id in self.display_manager.get_annotation_holder().get_image_canvas().find_all()[1:]:
            self.display_manager.get_annotation_holder().get_image_canvas().itemconfig(object_id, state='hidden')

    def show_annotations(self):
        for object_id in self.display_manager.get_annotation_holder().get_image_canvas().find_all()[1:]:
            self.display_manager.get_annotation_holder().get_image_canvas().itemconfig(object_id, state='normal')

    def clear_annotations(self):
        if self.has_annotations():
            confirmation = messagebox.askyesno("Confirmation", "Are you sure to clear all annotations?")
            if confirmation:
                # extract object ids from the canvas, except the first one (image itself)
                annotation_object_ids = self.display_manager.get_annotation_holder().get_image_canvas().find_all()[1:] # type: ignore
                if len(annotation_object_ids) > 0:
                    for object_id in annotation_object_ids:
                        self.display_manager.get_annotation_holder().get_image_canvas().delete(object_id)
                    self.clear_annotation_set()
                    self.coordinator.reset_annotation_stats()
                    self.bind_annotation_keys()
                    self.state_manager.set_annotations_on_display()
                    self._update_toggle_button_visibility()

    def clear_annotation_set(self):
        annotation_set = self._get_annotation_set()
        if annotation_set is not None:
            annotation_set.clear()

    def get_active_annotation_type(self):
        annotation_type_var = self.coordinator.get_var_annotation_type()
        if annotation_type_var is not None:
            return annotation_type_var.get()
        else:
            raise ValueError("Annotation type variable is None")

    def get_annotations_count(self, belonging_group_label: str | None = None):
        return self._get_annotation_set().get_count(belonging_group_label)

    def has_annotations(self):
        return self.get_annotations_count() > 0

    def _get_annotation_object_identifier(self, annotation_type: str):
        annotation_object_dictionary = {
            'circle': 0,
            'cross_mark': 1
        }
        return annotation_object_dictionary.get(annotation_type, -1)

    def _generate_annotation_object(
        self,
        center_coords_on_roi: tuple[int, int],
        center_coords_on_canvas: tuple[int, int],
        object_id: int
    ) -> AnnotationObjectInterface:
        suitable_object_sizes_on_canvas = self.get_suitable_object_sizes(on='canvas')
        suitable_object_sizes_on_roi = self.get_suitable_object_sizes(on='roi')
        if object_id == 0:
            return AnnotationCircle(
                center_coord_on_roi = center_coords_on_roi,
                center_coord_on_canvas = center_coords_on_canvas,
                size_on_canvas = suitable_object_sizes_on_canvas.get(AnnotationCircle.get_name_label(), AnnotationCircle.get_default_size_on_canvas()),
                size_on_roi = suitable_object_sizes_on_roi.get(AnnotationCircle.get_name_label(), AnnotationCircle.get_default_size_on_roi()),
                belonging_group_label=str(object_id)
            )
        elif object_id == 1:
            return AnnotationCrossMark(
                center_coord_on_roi = center_coords_on_roi,
                center_coord_on_canvas = center_coords_on_canvas,
                size_on_canvas=suitable_object_sizes_on_canvas.get(AnnotationCrossMark.get_name_label(
                ), AnnotationCrossMark.get_default_size_on_canvas()),
                size_on_roi=suitable_object_sizes_on_roi.get(AnnotationCrossMark.get_name_label(
                ), AnnotationCrossMark.get_default_size_on_roi()),
                belonging_group_label=str(object_id)
            )
        else:
            raise ValueError("Invalid annotation type.")

    def _check_if_annotation_has_overlap(self, center_coords: tuple[int, int], on: Literal['roi', 'canvas'] ) -> bool:
        if self.has_annotations():
            annotation_objects = self._get_annotation_objects()
            for annotation in annotation_objects:
                center_x, center_y = annotation.get_geometric_coords(on).get('center')
                width, height = annotation.get_geometric_coords(on).get('width'), annotation.get_geometric_coords(on).get('height')
                if (center_coords[0] >= center_x - width/2) and (center_coords[0] <= center_x + width/2):
                    if (center_coords[1] >= center_y - height/2) and (center_coords[1] <= center_y + height/2):
                        return True
        return False

    def _check_if_annotation_is_within_image(self, center_coords: tuple[int, int]) -> bool:
        # avoid placing annotations outside the image area on the canvas
        image_entity = self.display_manager.get_annotation_holder().get_image_entity()
        if image_entity is not None and image_entity.has_numeric_dimensions():
            image_width, image_height = image_entity.get_dimensions_resized()
            # considering that image is centered on the canvas
            canvas_width, canvas_height = self.display_manager.get_canvas_size()
            extra_x = (canvas_width - image_width) / 2
            extra_y = (canvas_height - image_height) / 2
            annotation_x, annotation_y = center_coords
            if (annotation_x >= 0) and (annotation_x >= extra_x) and (annotation_x <= canvas_width - extra_x):
                if (annotation_y >= 0) and (annotation_y >= extra_y) and (annotation_y <= canvas_height - extra_y):
                    return True
        return False

    def _update_toggle_button_visibility(self):
        if self.has_annotations():
            self.layout_manager.show_button_toggle_annotations()
        else:
            self.layout_manager.hide_button_toggle_annotations()

    def _on_roi_left_click(self, event):
        annotation_set = self._get_annotation_set()
        if annotation_set is None:
            raise ValueError("No annotation set is initialized, please register the annotation set first.")
        # clicking point should be within the image area and not overlapping with existing annotations
        center_on_canvas = (event.x, event.y)
        center_on_roi = self.map_coordinate_points(center_on_canvas)
        if self._check_if_annotation_is_within_image(center_on_canvas) and not self._check_if_annotation_has_overlap(center_coords=center_on_canvas, on='canvas'):
            annotation_obj = self._generate_annotation_object(
                center_coords_on_roi = center_on_roi,
                center_coords_on_canvas = center_on_canvas,
                object_id = self.get_active_annotation_type()
            )
            annotation_obj.draw_on_canvas(self.display_manager.get_annotation_holder().get_image_canvas()) # type: ignore
            annotation_set.add_object(annotation_obj)
            self._update_annotation_stats()
            self._update_toggle_button_visibility()

    def _on_roi_right_click(self, event):
        target_ann_type_id = self.get_active_annotation_type()
        annotation_objects = self._get_annotation_objects(
            belonging_group_label=str(target_ann_type_id)
        )
        if len(annotation_objects) > 0:
            # check if the click is within the bounds of an annotation
            event_x, event_y = event.x, event.y
            for annotation in annotation_objects:
                center_x, center_y = annotation.get_geometric_coords(on='canvas').get('center')
                width, height = annotation.get_geometric_coords(on='canvas').get('width'), annotation.get_geometric_coords(on='canvas').get('height')
                if (event_x >= center_x - width/2) and (event_x <= center_x + width/2):
                    if (event_y >= center_y - height/2) and (event_y <= center_y + height/2):
                        print("Annotation removal triggered.")
                        self.display_manager.get_annotation_holder().get_image_canvas().delete(annotation.get_entity_id())
                        self._get_annotation_set().remove_object(annotation)
                        self._update_annotation_stats()
                        break
            self._update_toggle_button_visibility()

    def _update_annotation_stats(self, type_id: int | None = None):
        target_ann_type_id = type_id if type_id is not None else self.get_active_annotation_type()
        self.coordinator.set_var_annotations_count(
            annotation_type_id = target_ann_type_id,
            value = self.get_annotations_count(belonging_group_label = str(target_ann_type_id))
        )


    # ************************************************
    def change_in_environment_detected(self, crop_size: tuple[int, int], canvas_size: tuple[int, int]) -> bool:
        return True if (crop_size != self.coordinator.get_var_cutout_size()) or (canvas_size != self.display_manager.get_canvas_size()) else False

    def remap_annotation_coordinates(
        self,
        annotations: list[AnnotationObjectInterface],
        original_crop_size: tuple[int, int],
        original_canvas_size: tuple[int, int]
    ) -> None:
        """
        Remaps annotation coordinates when environmental parameters (crop size, canvas size) have changed.

        Args:
            annotations: List of annotation objects to apply remapping to
            original_crop_size: Original ROI crop size (width, height) when annotations were created
            original_canvas_size: Original canvas size (width, height) when annotations were created

        Returns:
            None (modifies the annotation objects in-place)
        """
        # get current environment parameters
        current_crop_size = self.coordinator.get_var_cutout_size()
        current_canvas_size = self.display_manager.get_canvas_size()

        # calculate scaling factors between original and current environment
        width_scale_crop = current_crop_size[0] / \
            original_crop_size[0] if original_crop_size[0] > 0 else 1.0
        height_scale_crop = current_crop_size[1] / \
            original_crop_size[1] if original_crop_size[1] > 0 else 1.0

        width_scale_canvas = current_canvas_size[0] / \
            original_canvas_size[0] if original_canvas_size[0] > 0 else 1.0
        height_scale_canvas = current_canvas_size[1] / \
            original_canvas_size[1] if original_canvas_size[1] > 0 else 1.0

        # get suitable sizes for annotations in the current environment
        suitable_object_sizes_on_canvas = self.get_suitable_object_sizes(on='canvas')
        suitable_object_sizes_on_roi = self.get_suitable_object_sizes(on='roi')

        # remapped_annotations = []
        for annotation in annotations:
            # get original coordinates
            geometric_coords_roi = annotation.get_geometric_coords(on='roi')
            geometric_coords_canvas = annotation.get_geometric_coords(on='canvas')
            if geometric_coords_roi is None or geometric_coords_canvas is None:
                continue
            original_coords_on_roi = geometric_coords_roi.get('center', ())
            original_coords_on_canvas = geometric_coords_canvas.get('center', ())

            # calculate new coordinates
            new_coords_on_roi = (
                int(round(original_coords_on_roi[0] * width_scale_crop)),
                int(round(original_coords_on_roi[1] * height_scale_crop))
            )

            new_coords_on_canvas = (
                int(round(original_coords_on_canvas[0] * width_scale_canvas)),
                int(round(original_coords_on_canvas[1] * height_scale_canvas))
            )

            # ensure coordinates are within bounds
            current_width, current_height = current_crop_size
            new_coords_on_roi = (
                max(0, min(new_coords_on_roi[0], current_width - 1)),
                max(0, min(new_coords_on_roi[1], current_height - 1))
            )

            canvas_width, canvas_height = current_canvas_size
            new_coords_on_canvas = (
                max(0, min(new_coords_on_canvas[0], canvas_width - 1)),
                max(0, min(new_coords_on_canvas[1], canvas_height - 1))
            )

            # modify annotation object with new coordinates and dimensional properties
            annotation.set_center_coord_on_roi(new_center_coord=new_coords_on_roi)
            annotation.set_center_coord_on_canvas(new_center_coord=new_coords_on_canvas)
            # annotation.rescale_dimensions(factor=width_scale_canvas)
            annotation.set_size(
                size = suitable_object_sizes_on_roi.get(annotation.get_name_label(), annotation.get_default_size_on_roi()),
                on='roi'
            )
            annotation.set_size(
                size=suitable_object_sizes_on_canvas.get(annotation.get_name_label(), annotation.get_default_size_on_canvas()),
                on='canvas'
            )

            # object_id = int(annotation.get_belonging_group_label())
            # new_annotation = self._generate_annotation_object(
            #     center_coords_on_roi=new_coords_on_roi,
            #     center_coords_on_canvas=new_coords_on_canvas,
            #     object_id=object_id
            # )


    def import_from_analysis_dots(self, bbox_coords: list[tuple[float, float, float, float]]):
        annotation_set = self._get_annotation_set()
        scale_ratio_width, scale_ratio_height = self.display_manager.get_roi_holder().get_image_entity().get_resize_ratio() # type: ignore
        # consider empty space around the image on the canvas (if any)
        extra_x = (self.display_manager.get_canvas_size()[0] - self.display_manager.get_roi_holder().get_image_entity().get_dimensions_resized()[0]) / 2
        extra_y = (self.display_manager.get_canvas_size()[1] - self.display_manager.get_roi_holder().get_image_entity().get_dimensions_resized()[1]) / 2
        for bbox in bbox_coords:
            x0, y0, x1, y1 = bbox
            center_x = int((x0 + x1) / 2)
            center_y = int((y0 + y1) / 2)
            center_on_roi = (int(center_x), int(center_y))
            center_on_canvas = (int(round(center_x * scale_ratio_width) + extra_x), int(round(center_y * scale_ratio_height) + extra_y))
            if not self._check_if_annotation_has_overlap(center_coords=center_on_canvas, on='canvas'):
                annotation_obj = self._generate_annotation_object(
                    center_coords_on_roi = center_on_roi,
                    center_coords_on_canvas = center_on_canvas,
                    object_id = self._get_annotation_object_identifier('circle')
                )
                annotation_obj.draw_on_canvas(self.display_manager.get_annotation_holder().get_image_canvas()) # type: ignore
                annotation_set.add_object(annotation_obj)
                self._update_annotation_stats(self._get_annotation_object_identifier('circle'))
        self._update_toggle_button_visibility()

    def import_from_analysis_branches(self, bbox_coords: list[tuple[float, float, float, float]]):
        annotation_set = self._get_annotation_set()
        scale_ratio_width, scale_ratio_height = self.display_manager.get_roi_holder().get_image_entity().get_resize_ratio() # type: ignore
        # consider empty space around the image on the canvas (if any)
        extra_x = (self.display_manager.get_canvas_size()[0] - self.display_manager.get_roi_holder().get_image_entity().get_dimensions_resized()[0]) / 2
        extra_y = (self.display_manager.get_canvas_size()[1] - self.display_manager.get_roi_holder().get_image_entity().get_dimensions_resized()[1]) / 2
        for bbox in bbox_coords:
            x0, y0, x1, y1 = bbox
            center_x = int((x0 + x1) / 2)
            center_y = int((y0 + y1) / 2)
            center_on_roi = (int(center_x), int(center_y))
            center_on_canvas = (int(round(center_x * scale_ratio_width) + extra_x), int(round(center_y * scale_ratio_height) + extra_y))
            if not self._check_if_annotation_has_overlap(center_coords=center_on_canvas, on='canvas'):
                annotation_obj = self._generate_annotation_object(
                    center_coords_on_roi = center_on_roi,
                    center_coords_on_canvas = center_on_canvas,
                    object_id = self._get_annotation_object_identifier('cross_mark')
                )
                annotation_obj.draw_on_canvas(self.display_manager.get_annotation_holder().get_image_canvas()) # type: ignore
                annotation_set.add_object(annotation_obj)
                self._update_annotation_stats(self._get_annotation_object_identifier('cross_mark'))
        self._update_toggle_button_visibility()

    def check_for_annotation_file(self):
        roi_path = self.display_manager.get_roi_image().get_file_path()
        ann_path = f"{roi_path.rsplit('.', 1)[0]}.{self.annotation_file_extension}"
        if self.file_manager.file_exists(ann_path):
            ann_metadata = self.file_manager.read_object(ann_path)
            ann_list = ann_metadata.get('annotations', [])
            if len(ann_list) > 0:
                annotation_set = self._get_annotation_set()
                ann_objects : list[AnnotationObjectInterface] = self._build_annotations_from_saved_data(
                    annotation_data = ann_list
                )
                # remap the coordinates if the environment has changed
                if self.change_in_environment_detected(
                    crop_size=ann_metadata.get('roi_crop_size'),
                    canvas_size=ann_metadata.get('roi_canvas_size')
                ):
                    self.remap_annotation_coordinates(
                        annotations=ann_objects,
                        original_crop_size=ann_metadata.get('roi_crop_size'),
                        original_canvas_size=ann_metadata.get('roi_canvas_size')
                    )
                # draw the annotations on the canvas, add them to the annotation set and update the stats
                for annotation in ann_objects:
                    annotation.draw_on_canvas(self.display_manager.get_annotation_holder().get_image_canvas()) # type: ignore
                    annotation_set.add_object(annotation)
                    self._update_annotation_stats(int(annotation.get_belonging_group_label())) # type: ignore
                self._update_toggle_button_visibility()
                self.layout_manager.focus_on_annotation_tab()


    # ************************************************
    def get_annotation_file_extension(self):
        return self.annotation_file_extension

    def _safe_load_annotation_font(self, size: int | float):
        """
        Load an annotation font with cross-platform fallbacks.
        Selects an OS-specific ordered list of font candidates.
        """
        normalized_size = max(8, int(size))
        # prepare OS-specific font candidate lists
        if self.coordinator.os_is_windows():
            font_candidates = [
                "seguiemj.ttf",           # Segoe UI Emoji (Windows)
                "Segoe UI Emoji.ttf",
                "Segoe UI Symbol.ttf",
                "Arial.ttf",
                "Tahoma.ttf",
            ]
        elif self.coordinator.os_is_mac():
            font_candidates = [
                "Apple Color Emoji.ttf",  # macOS emoji
                "Helvetica.ttc",          # macOS system
                "Arial.ttf",
                "Menlo.ttc",
            ]
        elif self.coordinator.os_is_linux():
            font_candidates = [
                "NotoColorEmoji.ttf",    # Noto Color Emoji
                "NotoSansSymbols2.ttf",  # Noto Sans Symbols (comprehensive symbol support)
                "NotoSansSymbols.ttf",   # Noto Sans Symbols (alternative)
                "DejaVuSans.ttf",        # common on Linux
                "FreeSans.ttf",
                "Arial.ttf",
            ]
        else:
            font_candidates = ["DejaVuSans.ttf", "Arial.ttf"]

        for font_name in font_candidates:
            try:
                return ImageFont.truetype(font_name, normalized_size)
            except OSError:
                continue

        # last resort: Pillow default bitmap font
        return ImageFont.load_default()


    def _save_annotated_image(self, image: Image.Image, output_path: str):
        """
        Save image with quality options, and fall back to safer defaults when unavailable.
        """
        try:
            image.save(output_path, quality=95, optimize=True, dpi=(300, 300))
        except OSError:
            image.save(output_path, quality=95, dpi=(300, 300))

    def _prepare_annotations_for_saving(self, annotation_set: AnnotationSet):
        serializable_annotations = []
        for annotation in annotation_set:
            serializable_annotations.append(annotation.get_serialized_data())
        return serializable_annotations

    def _create_metadata_object_for_saving(self, annotation_set: AnnotationSet):
        screen_resolution = self.display_manager.get_screen_resolution()
        roi_canvas_size = self.display_manager.get_canvas_size()
        roi_crop_size = self.coordinator.get_var_cutout_size()
        roi_coords_on_WSI = self.display_manager.get_roi_coords() if self.state_manager.is_roi_from_source() else None
        wsi_file_info = self.display_manager.get_source_holder().get_image_file_info() if self.state_manager.is_roi_from_source() else None
        annotations = self._prepare_annotations_for_saving(annotation_set)
        metadata = {
            'screen_resolution': screen_resolution,
            'roi_canvas_size': roi_canvas_size,
            'roi_crop_size': roi_crop_size,
            'roi_coords_on_WSI': roi_coords_on_WSI,
            'wsi_file_info': wsi_file_info,
            'annotations': annotations
        }
        return metadata

    def _build_annotations_from_saved_data(self, annotation_data: list[dict]) -> list[AnnotationObjectInterface]:
        annotations = []
        for annotation_dict in annotation_data:
            center_coords_on_canvas = annotation_dict['center_coord_on_canvas']
            center_coords_on_roi = annotation_dict['center_coord_on_roi']
            object_type_id = int(annotation_dict['belonging_group_label'])
            annotation_obj = self._generate_annotation_object(
                center_coords_on_roi = center_coords_on_roi,
                center_coords_on_canvas = center_coords_on_canvas,
                object_id = object_type_id
            )
            annotation_obj.set_color(annotation_dict['color'])
            annotation_obj.set_size(annotation_dict['size_on_roi'], 'roi')
            annotation_obj.set_size(annotation_dict['size_on_canvas'], 'canvas')
            annotations.append(annotation_obj)
        return annotations

    def trigger_export(self):
        # make corresponding folder if it does not exist
        current_path = self.display_manager.get_roi_image().get_file_dir()
        file_name = self.display_manager.get_roi_image().get_file_name()
        file_name_raw = file_name.rsplit(".", 1)[0]
        if self.state_manager.is_roi_from_source():
            target_dir = f"{current_path}/{file_name_raw}"
            self.file_manager.create_dir(
                dir_path = target_dir
            )
            prefix_str = self.file_manager.get_identifier_for_cutout_images()
        else:
            target_dir = current_path
            prefix_str = ""

        # save cut-out with prefix name
        save_path = self.file_manager.save_image_via_dialog(
            image_array = self.display_manager.get_roi_image().get_np_image(),
            window_title = "Export...",
            save_dir = target_dir,
            file_name = file_name,
            additional_prefix = prefix_str
        )
        print(f"Cut-out saved to: {save_path}")

        # if there are annotations, save them as well
        if self.has_annotations() and save_path is not None:
            # update target directory based on the (new) save path
            target_dir = save_path.rsplit("/", 1)[0]
            ann_file_name_raw = save_path.rsplit("/", 1)[1].rsplit(".", 1)[0]
            # ann_file_name = ann_file_name_raw + self.annotation_file_extension
            # ann_save_path = f"{target_dir}/{ann_file_name}"
            self.file_manager.save_object(
                obj = self._create_metadata_object_for_saving(self._get_annotation_set()),
                dir_path = target_dir,
                file_name = ann_file_name_raw,
                file_extension = self.annotation_file_extension
            )
            print(f"Metadata also saved alongside the raw cut-out and annotated image, by the following name: {ann_file_name_raw}.{self.annotation_file_extension}")


            # save annotated image

            # ann_img = self.display_manager.get_roi_image().get_np_image().copy()
            # resize_width, resize_height = self.display_manager.get_roi_holder().get_image_entity().get_dimensions_resized()
            # scale_ratio_width, scale_ratio_height = self.display_manager.get_roi_holder().get_image_entity().get_resize_ratio() # type: ignore
            # ann_img = expand_channel(ann_img)
            # im_pil = Image.fromarray(obj=ann_img, mode="RGB")
            # im_pil = im_pil.resize((resize_width, resize_height))
            # draw_pad = ImageDraw.Draw(im_pil)
            # marking_size_circle = 13.2 * scale_ratio_width
            # marking_size_crossmark = 7 * scale_ratio_width
            # marking_font_circle = ImageFont.truetype("seguiemj.ttf", marking_size_circle)
            # marking_font_crossmark = ImageFont.truetype("seguiemj.ttf", marking_size_crossmark)
            # tick_circle = str("●")
            # tick_crossmark = str("✖️")
            # # print(ann_img.shape, resize_width, resize_height)

            # annotation_objects = self._get_annotation_objects()
            # for annotation in annotation_objects:
            #     center_x, center_y = annotation.get_geometric_coords(on='canvas').get('center')
            #     if annotation.get_belonging_group_label() == '0':
            #         center_x, center_y = int(center_x - marking_size_circle/2), int(center_y - marking_size_circle/2)
            #         draw_pad.text((center_x, center_y), tick_circle, fill=self.color_circles, font=marking_font_circle, align='center')
            #         # print(f"Annotated circle at: {center_x}, {center_y}")
            #     elif annotation.get_belonging_group_label() == '1':
            #         center_x, center_y = int(center_x - marking_size_crossmark/2), int(center_y - marking_size_crossmark/2)
            #         draw_pad.text((center_x, center_y), tick_crossmark, fill=self.color_crossmarks, font=marking_font_crossmark, align='center')

            # resize_back_width, resize_back_height = self.display_manager.get_roi_holder().get_image_entity().get_dimensions()
            # im_pil = im_pil.resize((resize_back_width, resize_back_height))
            # im_pil.save(f"{target_dir}/{ann_file_name_raw}_annotated.{self.file_manager.get_default_save_extension_annotation()}")



            ann_img = self.display_manager.get_roi_image().get_np_image().copy()
            ann_img = expand_channel(ann_img)
            im_pil = Image.fromarray(obj=ann_img, mode="RGB")
            draw_pad = ImageDraw.Draw(im_pil)
            # roi_size = self.coordinator.get_var_cutout_size()[0]
            # marking_size_circle = roi_size / 22.7272  # 13.2
            marking_size_circle = self.get_suitable_object_sizes(on='roi').get(AnnotationCircle.get_name_label(), AnnotationCircle.get_default_size_on_roi())[1]
            # marking_size_crossmark = roi_size / 42.857  # 7
            marking_size_crossmark = self.get_suitable_object_sizes(on='roi').get(AnnotationCrossMark.get_name_label(), AnnotationCrossMark.get_default_size_on_roi())[1]
            marking_font_circle = self._safe_load_annotation_font(marking_size_circle)
            marking_font_crossmark = self._safe_load_annotation_font(marking_size_crossmark)
            tick_circle = str("●")
            tick_crossmark = str("✖️")

            annotation_objects = self._get_annotation_objects()
            for annotation in annotation_objects:
                center_x, center_y = annotation.get_geometric_coords(on='roi').get('center')
                if annotation.get_belonging_group_label() == '0':
                    center_x, center_y = int(center_x - marking_size_circle/2), int(center_y - marking_size_circle/2)
                    draw_pad.text((center_x, center_y), tick_circle, fill=self.color_circles, font=marking_font_circle, align='center')
                    # print(f"Annotated circle at: {center_x}, {center_y}")
                elif annotation.get_belonging_group_label() == '1':
                    center_x, center_y = int(center_x - marking_size_crossmark/2), int(center_y - marking_size_crossmark/2)
                    draw_pad.text((center_x, center_y), tick_crossmark, fill=self.color_crossmarks, font=marking_font_crossmark, align='center')

            # save with high quality settings (with safe fallback for platform differences)
            self._save_annotated_image(
                image=im_pil,
                output_path=f"{target_dir}/{ann_file_name_raw}_annotated.{self.file_manager.get_default_save_extension_annotation()}"
            )
            # im_pil.save(f"{target_dir}/{ann_file_name_raw}_annotated.{self.file_manager.get_default_save_extension_annotation()}")
