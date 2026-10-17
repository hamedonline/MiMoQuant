import numpy as np
from PIL import Image, ImageTk
from typing import Literal
from utils.image.io import read_image_unicode
from utils.image.general import resize_image
from utils.file.io import generate_file_info



class ImageEntity:
    def __init__(
        self,
        image_path: str | None = None,
        image_array: np.ndarray | None = None,
        color_mode: Literal["rgb", "grayscale"] = "grayscale",
    ) -> None:
        self.clear_out()
        self.file_path = image_path
        self.file_info = generate_file_info(image_path) if image_path is not None else None
        self.color_mode = color_mode
        if (image_path is not None) and (image_array is not None):
            raise Exception("Both image_path and image_array cannot be provided at the same time.")
        if image_path is not None:
            self.import_from_file(image_path)
        if image_array is not None:
            self.import_from_array(image_array)


    def has_image_array(self) -> bool:
        return self.np_image is not None


    def get_image_array(self) -> np.ndarray | None:
        return self.np_image if self.has_image_array() else None


    def import_from_file(self, file_path: str) -> None:
        try:
            self.np_image = read_image_unicode(
                image_path = file_path,
                color_mode = self.color_mode
            )
            self.file_path = file_path
            self.file_info = generate_file_info(file_path)
            self.tk_image = ImageEntity.create_tk_image(self.np_image)
            self.__set_dimensions()
        except Exception as e:
            print(f"Error reading image from file: {e}")


    def import_from_array(self, image_array: np.ndarray) -> None:
        # self.np_image = copy.deepcopy(image_array)
        self.np_image = image_array.copy()
        self.tk_image = ImageEntity.create_tk_image(self.np_image)
        self.__set_dimensions()


    @staticmethod
    def create_from_file(image_path: str, color_mode: Literal["rgb", "grayscale"]) -> 'ImageEntity':
        img_obj = ImageEntity(image_path=image_path, image_array=None, color_mode=color_mode)
        return img_obj


    @staticmethod
    def create_from_array(image_array: np.ndarray) -> 'ImageEntity':
        img_obj = ImageEntity(image_path=None, image_array=image_array)
        return img_obj


    @staticmethod
    def create_blank(color_mode: Literal["rgb", "grayscale"]) -> 'ImageEntity':
        return ImageEntity(image_path=None, image_array=None, color_mode=color_mode)


    @staticmethod
    def create_tk_image(image_array: np.ndarray) -> ImageTk.PhotoImage:
        return ImageTk.PhotoImage(image = Image.fromarray(image_array))


    @staticmethod
    def extract_dimensions(image_array: np.ndarray) -> tuple[int, int]:
        # in form of a tuple (width, height)
        return image_array.shape[1], image_array.shape[0]


    def __set_dimensions(self) -> None:
        if self.np_image is not None:
            # self.width, self.height = self.np_image.shape[1], self.np_image.shape[0]
            self.height, self.width = self.get_image_array().shape[:2] # type: ignore
            self.aspect_ratio = self.width / self.height


    def resize(self, new_dimension: tuple[float, float], resize_type: Literal["scale", "pixel"]) -> None:
        resized_img = resize_image(
            image_array = self.np_image,
            new_dimension = new_dimension,
            resize_type = resize_type
        )
        self.np_image_resized = resized_img
        self.tk_image_resized = ImageEntity.create_tk_image(resized_img)


    def clear_out(self) -> None:
        self.np_image, self.tk_image = None, None
        self.np_image_resized, self.tk_image_resized = None, None
        self.aspect_ratio, self.width, self.height = None, None, None
        self.file_path, self.file_info = None, None


    def get_channels_count(self) -> int | None:
        return len(self.np_image.shape) if self.np_image is not None else None

    def get_np_image(self) -> np.ndarray | None:
        return self.np_image

    def get_np_image_resized(self) -> np.ndarray | None:
        return self.np_image_resized

    def get_tk_image(self) -> ImageTk.PhotoImage | None:
        return self.tk_image

    def get_tk_image_resized(self) -> ImageTk.PhotoImage | None:
        return self.tk_image_resized

    def has_numeric_dimensions(self) -> bool:
        return self.width is not None and self.height is not None

    def get_dimensions(self) -> tuple[int, int] | None:
        if self.width is not None and self.height is not None:
            return self.width, self.height
        return None

    def get_dimensions_resized(self) -> tuple[int, int] | None:
        if self.np_image_resized is not None:
            return self.np_image_resized.shape[1], self.np_image_resized.shape[0]
        return None

    def get_resize_ratio(self) -> tuple[float, float] | None:
        if self.has_numeric_dimensions() and self.get_dimensions_resized() is not None:
            width, height = self.get_dimensions() # type: ignore
            resized_width, resized_height = self.get_dimensions_resized()  # type: ignore
            return (resized_width / width, resized_height / height) # type: ignore
        return None

    def get_file_info(self) -> dict | None:
        return self.file_info

    def get_file_name(self) -> str | None:
        return self.file_info.get('name') if self.file_info is not None else None

    def get_file_size(self) -> int | None:
        return self.file_info.get('file_size') if self.file_info is not None else None

    def get_file_dir(self) -> str | None:
        return self.file_info.get('file_dir') if self.file_info is not None else None

    def get_file_path(self) -> str | None:
        return self.file_path if self.file_path is not None else None

    def set_file_path(self, file_path: str) -> None:
        self.file_path = file_path
        self.file_info = generate_file_info(file_path)
