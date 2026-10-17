import warnings
import numpy as np
from .plotting import draw_line



def generate_rectangle_points(
    size: tuple[int, int],
    center_point: tuple[int, int] | None = None,
    top_left_corner: tuple[int, int] | None = None
) -> dict[str, tuple[int, int]]:
    """
    Generates the four corner points of a rectangle given its size, and either its center point or top left corner.
    OpenCV coordinates system explanation: https://stackoverflow.com/a/25644503

    Args:
        size (tuple[int, int]): The width and height of the rectangle.
        center_point (tuple[int, int], optional): The coordinates (x,y) of the center of the rectangle. Defaults to None.
        top_left_corner (tuple[int, int], optional): The coordinates (x,y) of the top left corner of the rectangle. Defaults to None.

    Returns:
        dict[str, tuple[int, int]]: A dictionary containing coordinates of the four corner points of the rectangle.
            The keys are: "top_left", "top_right", "bottom_right", "bottom_left".

    Raises:
        ValueError: If neither center_point nor top_left_corner is provided, or if the size is negative.
        UserWarning: If both center_point and top_left_corner are provided, the function will utilize the center_point by default.
    """
    # either one of center_point or top_left_corner must be specified
    rectangle_width, rectangle_height = size
    if rectangle_width < 0 or rectangle_height < 0:
        raise ValueError("The size of the rectangle cannot be negative")
    if center_point is None and top_left_corner is None:
        raise ValueError(
            "Either center_point or top_left_corner must be specified")
    elif center_point is not None and top_left_corner is not None:
        warnings.warn("\n\
            Both center_point and top_left_corner are specified.\n\
            Only one of them should be provided.\n\
            center_point will be used as default.")

    if center_point is not None:
        center_x, center_y = center_point
        top_left = (center_x - int(rectangle_width/2),
                    center_y - int(rectangle_height/2))
        top_right = (center_x + int(rectangle_width/2),
                     center_y - int(rectangle_height/2))
        bottom_left = (center_x - int(rectangle_width/2),
                       center_y + int(rectangle_height/2))
        bottom_right = (center_x + int(rectangle_width/2),
                        center_y + int(rectangle_height/2))
    else:  # top_left_corner is used to generate the points
        if top_left_corner is None:
            raise ValueError("top_left_corner cannot be None")
        top_left_x, top_left_y = top_left_corner
        top_left = (top_left_x, top_left_y)
        top_right = (top_left_x + rectangle_width, top_left_y)
        bottom_left = (top_left_x, top_left_y + rectangle_height)
        bottom_right = (top_left_x + rectangle_width,
                        top_left_y + rectangle_height)

    return {
        'top_left': top_left,
        'top_right': top_right,
        'bottom_right': bottom_right,
        'bottom_left': bottom_left
    }


def draw_bounding_box(
    image: np.ndarray,
    box_size: tuple[int, int],
    center_point: tuple[int, int] | None = None,
    top_left_corner: tuple[int, int] | None = None,
    color: tuple[int, int, int] = (255, 0, 0),
    thickness: int = 1,
    style: str = "solid",
    dash_length: int = 20
) -> np.ndarray:
    """
    Draw a rectangular bounding box on an image, given its size and either its center point or top left corner.
    This function keeps the original image intact and returns a new image with the drawn bounding box.

    Args:
        image (np.ndarray): The image on which the bounding box will be drawn.
        box_size (tuple[int, int]): The width and height of the bounding box.
        center_point (tuple[int, int], optional): The coordinates (x,y) of the center of the bounding box. Defaults to None.
        top_left_corner (tuple[int, int], optional): The coordinates (x,y) of the top left corner of the bounding box. Defaults to None.
        color (tuple[int, int, int]): The rgb color value for the bounding box.
        thickness (int, optional): The thickness of the bounding box. Defaults to 1.
        style (str, optional): The style of the bounding box. Defaults to "solid".
            The following styles are available:
                "solid": A solid bounding box.
                "dashed": A dashed bounding box.
        dash_length (int, optional): The length of the dashes in pixels. Defaults to 10. Only applicable if style is "dashed".

    Returns:
        np.ndarray: The image with the drawn bounding box.
    """
    result_img = image.copy()

    points = generate_rectangle_points(
        size=box_size,
        center_point=center_point,
        top_left_corner=top_left_corner
    )
    keys_order = ['top_left', 'top_right', 'bottom_right', 'bottom_left']
    ordered_points = [points[key] for key in keys_order]

    for start_point, end_point in zip(ordered_points, ordered_points[1:]+[ordered_points[0]]):
        result_img = draw_line(
            image = result_img,
            point1 = start_point,
            point2 = end_point,
            color = color,
            thickness = thickness,
            style = style,
            dash_length = dash_length
        )

    return result_img