import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from utils.image.general import expand_channel
from utils.general import pick_color


def create_blank_image(width: int, height: int, color: str = "white") -> np.ndarray:
    """
    Creates a blank three-channel image.

    Args:
        width (int): The image width in pixels.
        height (int): The image height in pixels.
        color (str, optional): The image color, such as ``'red'``,
            ``'green'``, ``'blue'``, ``'yellow'``, ``'purple'``, or
            ``'turquoise'``. Defaults to ``'white'``.

    Returns:
        np.ndarray: A three-channel, unsigned 8-bit image filled with the
        specified color.
    """
    image = np.zeros((height, width, 3), np.uint8)
    image[:] = pick_color(c_name=color)
    return image


def plot_image(image_array, color_mode='rgb', fig_size=10, hide_axis=True, push_output=False):
    """
    Plots an image array.

    To display a single color channel, specify the channel through
    ``color_mode``.

    Args:
        image_array (np.ndarray): The image array to plot.
        color_mode (str, optional): The channels to display. Use ``'r'``,
            ``'g'``, or ``'b'`` for a single channel, or ``'rgb'`` for all
            channels. Defaults to ``'rgb'``.
        fig_size (int, optional): The figure width and height in inches.
            Defaults to ``10``.
        hide_axis (bool, optional): Whether to hide the axis ticks and
            labels. Defaults to ``True``.
        push_output (bool, optional): Whether to display the image in an
            operating-system window in addition to the Matplotlib figure.
            Defaults to ``False``.

    Returns:
        None: This function displays the image and does not return a value.
    """
    if (image_array.ndim == 2) or (image_array.shape[2] == 1):
        image_array = expand_channel(image_array)

    if color_mode == 'r':
        image_array[:, :, 1] = 0
        image_array[:, :, 2] = 0
    elif color_mode == 'g':
        image_array[:, :, 0] = 0
        image_array[:, :, 2] = 0
    elif color_mode == 'b':
        image_array[:, :, 0] = 0
        image_array[:, :, 1] = 0

    if push_output:
        cv.imshow('Image Plot', cv.cvtColor(image_array, cv.COLOR_RGB2BGR))
        cv.waitKey(0)
        cv.destroyAllWindows()
    fig = plt.figure(figsize=(fig_size, fig_size))
    ax = fig.add_subplot(111)
    if hide_axis:
        ax.axis('off')
    ax.imshow(image_array)


def plot_histogram(image_array):
    """
    Plots the histogram of an image array.

    Args:
        image_array (np.ndarray): The image array whose pixel-value
            distribution should be plotted.

    Returns:
        None: This function displays the histogram and does not return a
        value.
    """
    plt.hist(image_array.ravel(), 256, (0, 256))
    plt.show()


def check_line_style(style: str) -> bool:
    """
    Checks if the style is valid for line drawing.

    Args:
        style (str): The style of the line to be drawn.

    Returns:
        bool: True if the style is valid.

    Raises:
        ValueError: If the style is not valid.
    """
    valid_styles = ["solid", "dashed"]
    if style not in valid_styles:
        raise ValueError(
            f"Invalid line style. Only the following styles are valid: {valid_styles}")
    return True


def draw_horizontal_line(
    image: np.ndarray,
    starting_point: tuple[int, int],
    length: int,
    color: tuple[int, int, int] = (255, 0, 0),
    thickness: int = 1,
    style: str = "solid",
    dash_length: int = 10
) -> np.ndarray:
    """
    Draws a horizontal line on a given image.
    This function keeps the original image intact and returns a new image with the drawn line.

    Args:
        image (np.ndarray): The image on which the line will be drawn.
        starting_point (tuple[int, int]): The coordinates (x,y) of the starting point of the line.
        length (int): The length of the line in pixels.
        color (tuple[int, int, int], optional): The rgb color value for line. Defaults to None.
        thickness (int, optional): The thickness of the line. Defaults to 1.
        style (str, optional): The style of the line. Defaults to "solid".
            The following styles are available:
                "solid": A solid line.
                "dashed": A dashed line.
        dash_length (int, optional): The length of the dashes in pixels. Defaults to 10. Only applicable if style is "dashed".

    Returns:
        np.ndarray: The image with the drawn line.
    """
    if length == 0:
        return image
    check_line_style(style)

    result_img = image.copy()
    x_start, y = starting_point
    x_end = x_start + length
    # swap the start and end points if negative length is provided
    if x_start > x_end:
        x_start, x_end = x_end, x_start

    if style == "solid":
        cv.line(result_img, (x_start, y), (x_end, y), color, thickness)
    else: # dashed line
        for x in range(x_start, x_end, dash_length):
            cv.line(result_img, (x, y), (x+round(dash_length/2), y), color, thickness)

    return result_img


def draw_vertical_line(
    image: np.ndarray,
    starting_point: tuple[int, int],
    length: int,
    color: tuple[int, int, int] = (255, 0, 0),
    thickness: int = 1,
    style: str = "solid",
    dash_length: int = 10
) -> np.ndarray:
    """
    Draws a vertical line on a given image.
    This function keeps the original image intact and returns a new image with the drawn line.

    Args:
        image (np.ndarray): The image on which the line will be drawn.
        starting_point (tuple[int, int]): The coordinates (x,y) of the starting point of the line.
        length (int): The length of the line in pixels.
        color (tuple[int, int, int], optional): The rgb color value for the line. Defaults to None.
        thickness (int, optional): The thickness of the line. Defaults to 1.
        style (str, optional): The style of the line. Defaults to "solid".
            The following styles are available:
                "solid": A solid line.
                "dashed": A dashed line.
        dash_length (int, optional): The length of the dashes in pixels. Defaults to 10. Only applicable if style is "dashed".

    Returns:
        np.ndarray: The image with the drawn line.
    """
    if length == 0:
        return image
    check_line_style(style)

    result_img = image.copy()
    x, y_start = starting_point
    y_end = y_start + length
    # swap the start and end points if negative length is provided
    if y_start > y_end:
        y_start, y_end = y_end, y_start

    if style == "solid":
        cv.line(result_img, (x, y_start), (x, y_end), color, thickness)
    else: # dashed line
        for y in range(y_start, y_end, dash_length):
            cv.line(result_img, (x, y), (x, y+round(dash_length/2)), color, thickness)

    return result_img


def draw_line(
    image: np.ndarray,
    point1: tuple[int, int],
    point2: tuple[int, int],
    color: tuple[int, int, int] = (255, 0, 0),
    thickness: int = 1,
    style: str = "solid",
    dash_length: int = 10
) -> np.ndarray:
    """
    Draws a line between two points on a given image.
    This function keeps the original image intact and returns a new image with the drawn line.
    
    Args:
        image (np.ndarray): The image on which the line will be drawn.
        point1 (tuple[int, int]): The coordinates (x,y) of the first point.
        point2 (tuple[int, int]): The coordinates (x,y) of the second point.
        color (tuple[int, int, int], optional): The rgb color value for the line. Defaults to None.
        thickness (int, optional): The thickness of the line. Defaults to 1.
        style (str, optional): The style of the line. Defaults to "solid".
            The following styles are available:
                "solid": A solid line.
                "dashed": A dashed line. For the time being, only applicable if the line is either horizontal or vertical.
        dash_length (int, optional): The length of the dashes in pixels. Defaults to 10. Only applicable if style is "dashed".
    
    Returns:
        np.ndarray: The image with the drawn line.
    """
    x1, y1 = point1
    x2, y2 = point2
    result_img = image.copy()

    if x1 == x2: # vertical line
        starting_point = point1 if y1 < y2 else point2
        length = abs(y2 - y1)
        result_img = draw_vertical_line(
            image = result_img,
            starting_point = starting_point,
            length = length,
            color = color,
            thickness = thickness,
            style = style,
            dash_length = dash_length
        )
        
    elif y1 == y2: # horizontal line
        starting_point = point1 if x1 < x2 else point2
        length = abs(x2 - x1)
        result_img = draw_horizontal_line(
            image = result_img,
            starting_point = starting_point,
            length = length,
            color = color,
            thickness = thickness,
            style = style,
            dash_length = dash_length
        )

    else:  # oblique line (neither horizontal nor vertical)
        cv.line(result_img, point1, point2, color, thickness)
        # TODO: implement dashed oblique line
    
    return result_img


def draw_circle(
        image: np.ndarray,
        x: int, 
        y: int,
        r: int,
        fill: bool = True,
        value: int = 255,
        color: tuple | None = None
    ) -> np.ndarray:
    """
    Draws a circle on a copy of the given 2D or 3D numpy array (image).

    Args:
        image (np.ndarray): The original 2D or 3D image array. The input is
            not modified.
        x (int): The x-coordinate of the circle center.
        y (int): The y-coordinate of the circle center.
        r (int): The circle radius in pixels.
        fill (bool, optional): Whether to fill the circle. If ``False``, only
            the outline is drawn. Defaults to ``True``.
        value (int, optional): The intensity value used for grayscale images.
            Defaults to ``255``.
        color (tuple | None, optional): The RGB values used for color images.
            If ``None``, ``value`` is used. Defaults to ``None``.

    Returns:
        np.ndarray: A copy of the input image with the circle drawn.
    """
    # create a copy of the original image to work on
    new_image = image.copy()
    if color is not None and len(new_image.shape) == 2:
        new_image = cv.cvtColor(new_image, cv.COLOR_GRAY2BGR)

    h, w = new_image.shape[:2]

    # create a grid of coordinates
    Y, X = np.ogrid[:h, :w]

    # distance from the center (x, y)
    dist_from_center = np.sqrt((X - x)**2 + (Y - y)**2)

    if fill:
        # mask where the distance from the center is less than or equal to the radius
        mask = dist_from_center <= r
    else:
        # mask where the distance is exactly around the circle's edge (with some tolerance)
        mask = np.abs(dist_from_center - r) <= 1

    if color is not None and len(new_image.shape) == 3:
        # apply the mask to each channel if the image is in color
        for i in range(3):
            new_image[..., i][mask] = color[i]
    else:
        # apply the mask to the copied image and set the value
        new_image[mask] = value

    return new_image
