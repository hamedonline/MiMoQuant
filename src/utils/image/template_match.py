import cv2 as cv
import numpy as np
from utils.image.bbox import draw_bounding_box
from utils.image.general import expand_channel



def _check_method(method: int) -> bool:
    """
    Checks if the method is valid for template matching.

    Args:
        method (str): The method to be used for template matching. Should be one of Open`CV's template matching methods.

    Returns:
        bool: True if the method is valid.

    Raises:
        ValueError: If the method is not valid.
    """
    valid_methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED',
                     'cv.TM_CCORR', 'cv.TM_CCORR_NORMED',
                     'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
    method_ref = {method: eval(method) for method in valid_methods}
    if method not in method_ref.values():
        raise ValueError(
            f"Invalid method. Only the following methods are valid: {valid_methods}")
    return True


def _get_default_border_options() -> dict:
    """
    Returns the default border options for template matching.

    Returns:
        dict: The default border options.
    """
    return {
        'color': (255, 0, 0),
        'thickness': 2,
        'style': 'solid',
        'dash_length': 10
    }


def _check_border_options(border_options: dict) -> bool:
    """
    Checks if the border options are valid for template matching.

    Args:
        border_options (dict): The border options to be used for template matching.

    Returns:
        bool: True if the border options are valid.

    Raises:
        ValueError: If the provided border options are not valid.
    """
    valid_border_option_keys = ['color', 'thickness', 'style', 'dash_length']
    for option in border_options.keys():
        if option not in valid_border_option_keys:
            raise ValueError(
                f"Invalid border options config: Only the following keys are valid for provided options: {valid_border_option_keys}")
    return True


def template_match(
    image: np.ndarray,
    template: np.ndarray,
    method: str = 'TM_CCOEFF_NORMED',
    multiple_matching: bool = False,
    threshold: float = 0.8,
    border_options: dict = {}
) -> tuple[np.ndarray, list[dict]]:
    """
    Performs template matching on a given image using a specified method.

    Args:
        image (np.ndarray): The source image where the template will be searched in.
        template (np.ndarray): The template image that will be searched in the source image.
        method (str, optional): The method to be used for template matching. Defaults to 'TM_CCOEFF_NORMED'.
            The following methods are available via OpenCV template matching methods:
                'TM_CCOEFF': Correlation coefficient
                'TM_CCOEFF_NORMED': Normalized correlation coefficient
                'TM_CCORR': Cross-correlation
                'TM_CCORR_NORMED': Normalized cross-correlation
                'TM_SQDIFF': Sum of squared differences
                'TM_SQDIFF_NORMED': Normalized sum of squared differences
        multiple_matching (bool, optional): Whether to perform multiple matching. Defaults to False.
        threshold (float, optional): The threshold to be used for multiple matching. Defaults to 0.8.
        border_options (dict, optional): The border options to be used for drawing the bounding box around the matched template. Defaults to {}.
            The following options are valid keys for the dictionary:
                color (tuple[int, int, int]): The rgb color value for line. Defaults to (255, 0, 0).
                thickness (int): The thickness of the line. Defaults to 2.
                style (str): The style of the line. Defaults to "solid".
                    The following styles are available:
                        "solid": A solid line.
                        "dashed": A dashed line.
                dash_length (int): The length of the dashes in pixels. Defaults to 10. Only applicable if style is "dashed".
            e.g.:
                border_options = {
                    'color': (0, 255, 0),
                    'thickness': 2,
                    'style': 'dashed',
                    'dash_length': 10
                }

    Returns:
        tuple[np.ndarray, list[dict]]: A tuple containing the image with the bounding box around the matched template and a list of dictionaries, each containing information about a match. Each dictionary
                    includes the top-left corner coordinates of the match, the width and height of the matched template, and the match score.

    Raises:
        ValueError: If border options are not valid.
    """
    method_num = getattr(cv, method)
    if border_options:
        _check_border_options(border_options)

    img_3channel = expand_channel(image.copy())
    img_template_3channel = expand_channel(template.copy())
    img_gray = cv.cvtColor(img_3channel, cv.COLOR_RGB2GRAY)
    img_template_gray = cv.cvtColor(img_template_3channel, cv.COLOR_RGB2GRAY)
    marked_img = img_3channel.copy()
    matching_coords = []
    # h, w = template.shape
    # w, h = template.shape[::-1]1
    h, w = template.shape if template.ndim == 2 else template.shape[:2]

    result = cv.matchTemplate(img_gray, img_template_gray, method_num)
    if multiple_matching:
        result = cv.matchTemplate(img_gray, img_template_gray, method_num)
        loc = np.where(result >= threshold)
        # only keep one match per location (non-maximum suppression)
        selected_indices = cv.dnn.NMSBoxes(
            [list(pt) + [w, h] for pt in zip(*loc[::-1])], [float(r) for r in result[loc]], 0.5, 0.4
        )
        if len(selected_indices) > 0:
            for index in selected_indices:
                pt = (loc[1][index], loc[0][index])
                marked_img = draw_bounding_box(
                    image=marked_img,
                    box_size=(w, h),
                    top_left_corner=pt,
                    color=border_options.get('color', (255, 0, 0)),
                    thickness=border_options.get('thickness', 2),
                    style=border_options.get('style', 'solid'),
                    dash_length=border_options.get('dash_length', 10)
                )
                matching_coords.append(
                    {
                        'top_left': (int(pt[0]), int(pt[1])),
                        'width_height': (w, h),
                        'score': float(result[pt[1], pt[0]])
                    }
                )
    else:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        # if the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        top_left: tuple[int, int]
        if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
            top_left = min_loc  # type: ignore
        else:
            top_left = max_loc  # type: ignore
        # bottom_right = (top_left[0] + w, top_left[1] + h)
        marked_img = draw_bounding_box(
            image=marked_img,
            box_size=(w, h),
            top_left_corner=top_left,
            color=border_options.get('color', (255, 0, 0)),
            thickness=border_options.get('thickness', 2),
            style=border_options.get('style', 'solid'),
            dash_length=border_options.get('dash_length', 10)
        )
        matching_coords.append(
            {
                'top_left': (int(top_left[0]), int(top_left[1])),
                'width_height': (w, h),
                'score': float(max_val)
            }
        )

    return marked_img, matching_coords
