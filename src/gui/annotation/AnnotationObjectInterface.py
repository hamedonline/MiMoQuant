from typing import Literal
from abc import ABC, abstractmethod


class AnnotationObjectInterface(ABC):
    NAME_LABEL : str
    DEFAULT_SIZE_ON_CANVAS : tuple[int, int]
    DEFAULT_SIZE_ON_ROI : tuple[float, float]

    @classmethod
    def get_name_label(cls) -> str:
        return cls.NAME_LABEL

    @classmethod
    def get_default_size_on_canvas(cls) -> tuple[int, int]:
        return cls.DEFAULT_SIZE_ON_CANVAS

    @classmethod
    def get_default_size_on_roi(cls) -> tuple[float, float]:
        return cls.DEFAULT_SIZE_ON_ROI

    @abstractmethod
    def get_geometric_coords(self, on: Literal['roi', 'canvas']) -> dict:
        pass

    @abstractmethod
    def get_entity_id(self):
        pass

    @abstractmethod
    def get_color(self):
        pass

    @abstractmethod
    def get_parent_canvas(self):
        pass

    @abstractmethod
    def get_belonging_group_label(self):
        pass

    @abstractmethod
    def get_serialized_data(self):
        pass

    @abstractmethod
    def set_center_coord_on_roi(self, new_center_coord: tuple[int, int]):
        pass

    @abstractmethod
    def set_center_coord_on_canvas(self, new_center_coord: tuple[int, int]):
        pass
    
    @abstractmethod
    def set_color(self, color: str):
        pass

    @abstractmethod
    def set_size(self, size: tuple[int, int] | tuple[float, float], on: Literal['roi', 'canvas']):
        pass

    @abstractmethod
    def rescale_dimensions(self, factor: float):
        pass

    @abstractmethod
    def draw_on_canvas(self):
        pass