from tkinter import Canvas
from utils.entities.image_entity import ImageEntity



class CanvasEntity():
    def __init__(self, dimension: tuple[int, int] | None = None, padding: int=0, **kwargs):
        super().__init__()
        self.canvas_args = kwargs
        self.padding = padding
        if dimension is None: # if no dimensions are provided, it means canvas will be sized dynamically later, based on the drawing image dimensions
            # self.canvas_is_equal_to_image = True
            self.canvas_is_fixed_in_size = False
        else:
            # self.canvas_is_equal_to_image = False
            self.canvas_is_fixed_in_size = True
            self._set_dimensions(dimension)
        self._initialize_canvas()


    def _set_dimensions(self, dimension: tuple[int, int] | None) -> None:
        if dimension is not None:
            self.width, self.height = dimension
            self.aspect_ratio = self.width / self.height
            self.width += 2*self.padding
            self.height += 2*self.padding
        else:
            self.dimension = None
            self.aspect_ratio = None


    def _set_dimensions_from_image(self, image: ImageEntity) -> None:
        self._set_dimensions(image.get_dimensions())


    def _initialize_canvas(self) -> None:
        self.canvas = CanvasEntity.create_canvas(**self.canvas_args)
        # self.canvas.bind('<Configure>', self.__redraw_image)


    def _clear_canvas(self) -> None:
        self.canvas.delete('all')


    def has_image_reference(self) -> bool:
        return self.image_reference is not None


    def has_drawing_area(self) -> bool:
        return hasattr(self, 'canvas')


    def has_numeric_dimensions(self) -> bool:
        return self.width is not None and self.height is not None


    def get_dimensions(self) -> tuple[int, int] | None:
        if self.has_numeric_dimensions():
            return self.width, self.height
        return None


    def get_padding_size(self) -> int:
        return self.padding


    def get_canvas(self) -> Canvas:
        return self.canvas


    def get_postscript(self):
        self.canvas.update()
        return self.canvas.postscript(colormode='color')


    def close_canvas(self) -> None:
        if self.has_drawing_area():
            self._clear_canvas()
            self.canvas.grid_forget()
            # self.image_reference = None
            print("canvas cleared and closed.")


    @staticmethod
    def create_canvas(**kwargs) -> Canvas:
        return Canvas(**kwargs)


    def draw_image(self, image: ImageEntity) -> None:
        # if canvas size is fixed, the image should be resized to fit the canvas (and the aspect ratio of the image should remain intact)
        if self.canvas_is_fixed_in_size:
            resize_dimensions = self._calculate_image_resize_dimensions(image)
            if resize_dimensions is not None:
                resize_width, resize_height = resize_dimensions
                image.resize(new_dimension=(resize_width, resize_height), resize_type="pixel")
                image_to_draw = image.get_tk_image_resized()
        else:  # in case the canvas size is dynamic, canvas dimensions should be reconfigured based on the image size
            self._set_dimensions_from_image(image)
            image_to_draw = image.get_tk_image()
            self.canvas.bind('<Configure>', self._redraw_image)

        reconfig_dimensions = self.get_dimensions()
        if reconfig_dimensions is not None:
            reconfig_width, reconfig_height = reconfig_dimensions
            self.canvas.config(width=reconfig_width, height=reconfig_height)
        self._place_image(image_to_draw)
        self.image_reference = image


    def _calculate_image_resize_dimensions(self, image: ImageEntity) -> tuple[int, int] | None:
        if self.aspect_ratio is not None and image.aspect_ratio is not None:
            if self.aspect_ratio > image.aspect_ratio:  # when canvas is wider than the image
                resize_height = int(self.height - (2*self.padding))
                resize_width = int(resize_height * image.aspect_ratio)
            else: # when canvas is taller than the image
                resize_width = int(self.width - (2*self.padding))
                resize_height = int(resize_width / image.aspect_ratio)
            return resize_width, resize_height

    def _place_image(self, tk_img_obj) -> None:
        self._clear_canvas()
        x = (self.width) / 2
        y = (self.height) / 2
        self.canvas.create_image(x, y, image=tk_img_obj, anchor='center')
        self.canvas.update()
        self.canvas.grid()
        # self.canvas.grid(row=0, column=0, sticky='nsew')

    def _redraw_image(self, event) -> None:
        dynamic_width, dynamic_height = event.width, event.height
        # in order for image to fit the canvas properly, resizing should only be applied if the canvas has been preset with fixed dimensions
        if self.canvas_is_fixed_in_size:
            # calculate ratios and resize the image accordingly
            # scaled down/up the image to fit the canvas size
            return
        else: # if the canvas size is dynamic, it should be resized based on the parent container
            self._set_dimensions((dynamic_width, dynamic_height))
            resize_dimensions = self._calculate_image_resize_dimensions(self.image_reference)
            if resize_dimensions is not None:
                resize_width, resize_height = resize_dimensions
                self.image_reference.resize(new_dimension=(resize_width, resize_height), resize_type="pixel")
                self._place_image(self.image_reference.tk_image_resized)
