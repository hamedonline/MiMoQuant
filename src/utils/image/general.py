import os
import cv2
import numpy as np
from utils.image.filter import clahe
from typing import Literal
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"



def expand_channel(image_array, channel_factor=3):
    """
    Expands a one-channel grayscale image array to multiple channels.

    All channel values in the expanded image are identical.

    Args:
        image_array (np.ndarray): The input image array.
        channel_factor (int, optional): The number of channels in the
            expanded image. Defaults to ``3``.

    Returns:
        np.ndarray: The expanded image array, or the original array if it
        already contains multiple channels.
    """
    if (image_array.ndim == 2):
        return np.stack((image_array,)*channel_factor, axis=-1)
    elif image_array.shape[2] == 1:
        image_array = image_array[:, :, 0]
        return np.stack((image_array,)*channel_factor, axis=-1)
    else:
        return image_array


def extract_channel(image_array, color_mode='', threshold_mode='default', enhance_locally=False):
    """
    Extracts values of a single channel from the given numpy image array.

    Args:
        image_array (np.ndarray): The input image array.
        color_mode (str, optional): The channel or image representation to
            extract. Supported values are ``'r'``, ``'g'``, ``'b'``,
            ``'grayscale'``, and ``'binary'``. Defaults to ``''``.
        threshold_mode (str, optional): The threshold calculation mode used
            when ``color_mode`` is ``'binary'``. Supported values are
            ``'avg'``, ``'std'``, and ``'default'``. Defaults to
            ``'default'``.
        enhance_locally (bool, optional): Whether to apply CLAHE enhancement
            to the grayscale image when ``color_mode`` is ``'binary'``.
            Defaults to ``False``.

    Returns:
        np.ndarray: The extracted channel or transformed image. If
        ``color_mode`` is unsupported or empty, returns the input image array.
    """
    # check image channel(s) and expand, if it is single channeled
    image_array = expand_channel(image_array)

    if (color_mode == 'r') and (image_array.ndim == 3):
        return cv2.extractChannel(image_array, 0)
    elif color_mode == 'g' and (image_array.ndim == 3):
        return cv2.extractChannel(image_array, 1)
    elif color_mode == 'b' and (image_array.ndim == 3):
        return cv2.extractChannel(image_array, 2)
    elif color_mode == 'grayscale':
        return cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    elif color_mode == 'binary':
        # https://stackoverflow.com/a/42434377
        image_array_gs = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        image_array_gs = np.array(image_array_gs, dtype=np.float64)

        gs_median = int(np.median(image_array_gs))
        gs_mean   = int(np.mean(image_array_gs))
        gs_avg    = (gs_median + gs_mean) / 2
        gs_std    = int(np.std(image_array_gs))

        if threshold_mode == 'avg':
            threshold = gs_avg - int((255 - gs_avg) * 0.34)
        elif threshold_mode == 'std':
            threshold = int(gs_avg - (1.0 * gs_std))
        else: # 'default'
            threshold = 128

        if enhance_locally:
            image_array_gs = clahe(image_array_gs, clip_limit=2.0, tile_size=(16,16))
        return cv2.threshold(image_array_gs, threshold, 255, cv2.THRESH_BINARY)[1]

    else:
        return image_array


def threshold_image(image: np.ndarray, conditions: list[tuple[str, int, int]]) -> np.ndarray:
    """
    Applies a list of threshold conditions to an image.

    Args:
        image (np.ndarray): The input image array.
        conditions (list[tuple[str, int, int]]): Threshold conditions to
            apply. Each tuple contains an operator (``'<'``, ``'>'``,
            ``'<='``, ``'>='``, or ``'=='``), a value to compare against,
            and the result value to assign to matching pixels.

    Raises:
        ValueError: If an invalid operator is provided.

    Returns:
        np.ndarray: A new array with the threshold values applied.
    """

    # create a copy of the image to avoid modifying the original
    output = image.copy()

    for condition in conditions:
        # unpack the condition tuple
        operator, value, result = condition

        # create a boolean mask based on the operator and value
        if operator == '<':
            mask = image < value
        elif operator == '>':
            mask = image > value
        elif operator == '<=':
            mask = image <= value
        elif operator == '>=':
            mask = image >= value
        elif operator == '==':
            mask = image == value
        else:
            # invalid operator, raise an exception
            raise ValueError(f"Invalid operator: {operator}")

        # assign the result value to the output pixels that match the mask
        output[mask] = result

    return output


def threshold_image_adaptive(image: np.ndarray, adaptive_method: int, block_size: int) -> np.ndarray:
    thresh_img = cv2.adaptiveThreshold(
        src = image,
        maxValue = 255,
        adaptiveMethod = adaptive_method,
        thresholdType = cv2.THRESH_BINARY,
        blockSize = block_size,
        C = 0
    )
    return thresh_img


def calc_resolution(image_array, x_scale, y_scale):
    """
    Calculates an image's new resolution from scaling factors.

    Args:
        image_array (np.ndarray): The input image array.
        x_scale (float): The scaling factor along the x-axis.
        y_scale (float): The scaling factor along the y-axis.

    Returns:
        tuple[int, int]: The new image dimensions as ``(width, height)``.
    """
    width = int(image_array.shape[1] * x_scale)
    height = int(image_array.shape[0] * y_scale)
    return (width, height)


def calc_scale(image_array, width, height):
    """
    Calculates the proportional scale for a desired image size.

    Args:
        image_array (np.ndarray): The input image array.
        width (int): The desired image width in pixels.
        height (int): The desired image height in pixels.

    Returns:
        tuple[float, float]: The proportional scaling factors as
        ``(x_scale, y_scale)``.
    """
    x_scale = round(width / image_array.shape[1], 2)
    y_scale = round(height / image_array.shape[0], 2)
    return (x_scale, y_scale)


def resize_image(
        image_array,
        resize_type : Literal['scale', 'pixel'] = 'scale',
        new_dimension: tuple[float, float] = (1,1),
        max_quality=True
    ):
    """
    Resizes an image by scale factor or target pixel dimensions.

    When ``max_quality`` is ``True``, uses higher-quality interpolation
    methods for upscaling and downscaling.

    Args:
        image_array (np.ndarray): The input image array.
        resize_type (Literal['scale', 'pixel'], optional): Whether
            ``new_dimension`` specifies scale factors or pixel dimensions.
            Defaults to ``'scale'``.
        new_dimension (tuple[float, float], optional): The target dimensions
            as ``(width, height)``. Values are scale factors when
            ``resize_type`` is ``'scale'`` and pixel dimensions when it is
            ``'pixel'``. Defaults to ``(1, 1)``.
        max_quality (bool, optional): Whether to use higher-quality
            interpolation methods. Defaults to ``True``.

    Returns:
        np.ndarray: The resized image array.
    """
    if max_quality:
        upscale_itp   = cv2.INTER_CUBIC
        downscale_itp = cv2.INTER_AREA
    else:
        upscale_itp = cv2.INTER_NEAREST
        downscale_itp = cv2.INTER_NEAREST

    new_width, new_height = new_dimension

    if resize_type == 'scale':
        new_resolution = calc_resolution(image_array, new_width, new_height)
        if new_width > 1:
            return cv2.resize(image_array, new_resolution, interpolation=upscale_itp)
        else:
            return cv2.resize(image_array, new_resolution, interpolation=downscale_itp)

    elif resize_type == 'pixel':
        new_width, new_height = int(new_width), int(new_height)
        new_scale = calc_scale(image_array, new_width, new_height)
        if new_scale[0] > 1:
            return cv2.resize(image_array, (new_width, new_height), interpolation=upscale_itp)
        else:
            return cv2.resize(image_array, (new_width, new_height), interpolation=downscale_itp)


def proportional_resize(source_image_array, target_image_array, max_quality=True):
    """
    Resizes an image according to a target image's width and height.

    Args:
        source_image_array (np.ndarray): The image to resize.
        target_image_array (np.ndarray): The image whose dimensions are used
            as the resize target.
        max_quality (bool, optional): Whether to use higher-quality
            interpolation methods. Defaults to ``True``.

    Returns:
        np.ndarray: The resized source image, or the original source image if
        both images already have the same shape.
    """
    if source_image_array.shape != target_image_array.shape:
        target_height, target_width = target_image_array.shape[0], target_image_array.shape[1]
        return resize_image(source_image_array, resize_type='pixel', new_dimension=(target_width, target_height), max_quality=max_quality)
    return source_image_array


def equalize_dimensions(source_image_array, target_image_array, max_quality=True):
    """
    Equalizes an image's channels, height, and width to match a target image.

    Args:
        source_image_array (np.ndarray): The image to equalize.
        target_image_array (np.ndarray): The image whose dimensions and
            channel count are used as the target.
        max_quality (bool, optional): Whether to use higher-quality
            interpolation methods when resizing. Defaults to ``True``.

    Returns:
        np.ndarray: The source image with channel count and spatial
        dimensions matching the target image.
    """
    source_dim, target_dim = source_image_array.ndim, target_image_array.ndim

    # equalize channels
    if source_dim == target_dim:
        if source_dim == 3:
            if source_image_array.shape[2] != target_image_array.shape[2]:
                if source_image_array.shape[2] == 1: # target_image_array.shape[2] == 3
                    source_image_array = expand_channel(source_image_array, channel_factor=target_image_array.shape[2])
                else: # source_image_array.shape[2] == 3  ,  target_image_array.shape[2] == 1
                    source_image_array = extract_channel(source_image_array, color_mode='grayscale') # (h,w)
                    source_image_array = expand_channel(source_image_array, channel_factor=target_image_array.shape[2]) # (h,w,1)
    else: # source_dim != target_dim
        if source_dim == 2: # target_dim == 3
            source_image_array = expand_channel(source_image_array, channel_factor=target_image_array.shape[2])
        else: # source_dim == 3 , target_dim ==2
            source_image_array = extract_channel(source_image_array, color_mode='grayscale')

    # resize accordingly
    source_image_array = proportional_resize(source_image_array, target_image_array, max_quality)
    return source_image_array
