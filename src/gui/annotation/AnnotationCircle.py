from typing import Literal
from gui.annotation.AnnotationObjectInterface import AnnotationObjectInterface


class AnnotationCircle(AnnotationObjectInterface):
    __slots__ = ['_center_coord_on_roi', '_size_on_roi', '_width_on_roi', '_height_on_roi', '_radius_on_roi',
                 '_center_coord_on_canvas', '_size_on_canvas', '_width_on_canvas', '_height_on_canvas', '_radius_on_canvas',
                 '_color', '_entity_id', '_belonging_group_label', '_parent_canvas', '_coordinates_shift_on_canvas']

    NAME_LABEL = 'circle'
    DEFAULT_SIZE_ON_CANVAS = (18, 18)
    DEFAULT_SIZE_ON_ROI = (11.9, 11.9)

    def __init__(
        self,
        center_coord_on_roi: tuple[int, int],  # (x, y)
        center_coord_on_canvas: tuple[int, int],  # (x, y)
        size_on_canvas: tuple[int, int] = DEFAULT_SIZE_ON_CANVAS,  # (width, height)
        size_on_roi: tuple[float, float] = DEFAULT_SIZE_ON_ROI,  # (width, height)
        color: str = '#FF0000',
        belonging_group_label: str = '0'
    ) -> None:
        self._center_coord_on_roi = center_coord_on_roi
        self._center_coord_on_canvas = center_coord_on_canvas
        self.set_size(size_on_roi, on='roi')
        self.set_size(size_on_canvas, on='canvas')
        self._color = color
        self._belonging_group_label = belonging_group_label
        self._entity_id, self._parent_canvas = None, None
        self._coordinates_shift_on_canvas = (-3, -4) # for circle oval drawing
        # self._coordinates_fix_on_canvas = (-3, -6) # for circle text drawing


    @classmethod
    def get_name_label(cls):
        return cls.NAME_LABEL

    # @classmethod
    # def get_default_size(cls):
    #     return cls.DEFAULT_SIZE

    def _check_on_region_condition(self, on: Literal['roi', 'canvas']):
        if on not in {'roi', 'canvas'}:
            raise ValueError("'on' must be either 'roi' or 'canvas'")
    
    def get_geometric_coords(self, on: Literal['roi', 'canvas']) -> dict:
        """Get geometric coordinates based on the specified target (ROI or canvas)."""
        self._check_on_region_condition(on)
        return {
            "center": self.get_center_coord(on),
            "size": self.get_size(on),
            "width": self.get_width(on),
            "height": self.get_height(on),
            "radius": self.get_radius(on)
        }

    def get_entity_id(self):
        return self._entity_id

    def get_parent_canvas(self):
        return self._parent_canvas

    def get_color(self):
        return self._color

    def get_center_coord(self, on: Literal['roi', 'canvas']):
        self._check_on_region_condition(on)
        target = f"_on_{on}"
        return getattr(self, f"_center_coord{target}")

    def get_size(self, on: Literal['roi', 'canvas']):
        self._check_on_region_condition(on)
        target = f"_on_{on}"
        return getattr(self, f"_size{target}")

    def get_width(self, on: Literal['roi', 'canvas']):
        self._check_on_region_condition(on)
        target = f"_on_{on}"
        return getattr(self, f"_width{target}")

    def get_height(self, on: Literal['roi', 'canvas']):
        self._check_on_region_condition(on)
        target = f"_on_{on}"
        return getattr(self, f"_height{target}")

    def get_radius(self, on: Literal['roi', 'canvas']):
        self._check_on_region_condition(on)
        target = f"_on_{on}"
        return getattr(self, f"_radius{target}")

    def get_belonging_group_label(self):
        return self._belonging_group_label

    def get_serialized_data(self) -> dict:
        return {
            'type': self.get_name_label(),
            'color': self.get_color(),
            'belonging_group_label': self.get_belonging_group_label(),
            'center_coord_on_roi': self.get_center_coord(on='roi'),
            'center_coord_on_canvas': self.get_center_coord(on='canvas'),
            'size_on_roi': self.get_size(on='roi'),
            'size_on_canvas': self.get_size(on='canvas'),
        }

    def get_coordinates_shift_on_canvas(self):
        return self._coordinates_shift_on_canvas

    def set_center_coord_on_roi(self, new_center_coord):
        self._center_coord_on_roi = new_center_coord

    def set_center_coord_on_canvas(self, new_center_coord):
        self._center_coord_on_canvas = new_center_coord

    def set_parent_canvas(self, canvas):
        self._parent_canvas = canvas

    def set_color(self, color: str):
        self._color = color

    def set_size(self, size: tuple[int, int] | tuple[float, float], on: Literal['roi', 'canvas']):
        self._check_on_region_condition(on)
        target = f"_on_{on}"
        width, height = size
        setattr(self, f"_size{target}", size)
        setattr(self, f"_width{target}", width)
        setattr(self, f"_height{target}", height)
        setattr(self, f"_radius{target}", width // 2)

    def rescale_dimensions(self, factor: float):
        size_on_roi = self.get_size(on='roi')
        size_on_canvas = self.get_size(on='canvas')
        new_size_on_roi = (int(size_on_roi[0]*factor), int(size_on_roi[1]*factor))
        new_size_on_canvas = (int(size_on_canvas[0]*factor), int(size_on_canvas[1]*factor))
        self.set_size(new_size_on_roi, 'roi')
        self.set_size(new_size_on_canvas, 'canvas')

    def draw_on_canvas(self, canvas):
        self.set_parent_canvas(canvas)
        center_coord_on_canvas = self.get_center_coord(on='canvas')
        radius_on_canvas = self.get_radius(on='canvas')
        # coordinate fix => width:-3, height:-4
        self._entity_id = self._parent_canvas.create_oval( # type: ignore
            center_coord_on_canvas[0]-radius_on_canvas, center_coord_on_canvas[1]-radius_on_canvas,
            center_coord_on_canvas[0]+radius_on_canvas, center_coord_on_canvas[1]+radius_on_canvas,
            fill=self._color, stipple='gray50'
        )
        # # coordinate fix => width:-3, height:-6
        # # size fix factor: 1.618
        # width_on_canvas = self.get_width(on='canvas')
        # self._entity_id = self._parent_canvas.create_text(  # type: ignore
        #     center_coord_on_canvas[0]-3, center_coord_on_canvas[1]-6,
        #     text='●', fill=self.get_color(), font=('Arial', int(width_on_canvas*1.618), 'bold')
        # )
