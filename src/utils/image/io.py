import os
import cv2 as cv
import PIL.Image
import numpy as np
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def read_image(image_path, color_mode='rgb'):
    """
    Reads an image from disk and converts it to a NumPy array.

    For ``'rgb'`` mode, the returned array has shape
    ``(height, width, color_channels)`` with channels ordered as red, green,
    and blue. For ``'grayscale'`` mode, the returned array has shape
    ``(height, width)``.

    Args:
        image_path (str): The path to the image file.
        color_mode (str, optional): The desired color mode, either ``'rgb'``
            or ``'grayscale'``. Defaults to ``'rgb'``.

    Returns:
        np.ndarray: The image represented as a NumPy array.
    """
    if color_mode == 'grayscale':
        image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
    else:
        image = cv.imread(image_path)
        if(image.ndim == 3):
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    return image


def read_image_unicode(image_path, color_mode='rgb'):
    """
    Reads an image from disk and converts it to a NumPy array.

    This variant supports image paths containing Unicode characters. For
    ``'rgb'`` mode, the returned array has shape
    ``(height, width, color_channels)`` with channels ordered as red, green,
    and blue. For ``'grayscale'`` mode, the returned array has shape
    ``(height, width)``.

    Args:
        image_path (str): The path to the image file.
        color_mode (str, optional): The desired color mode, either ``'rgb'``
            or ``'grayscale'``. Defaults to ``'rgb'``.

    Returns:
        np.ndarray: The image represented as a NumPy array.
    """
    with open(image_path, "rb") as img_file:
        f = img_file.read()
        i = np.asarray(bytearray(f), dtype=np.uint8)

    if color_mode == 'grayscale':
        image = cv.imdecode(i, cv.IMREAD_GRAYSCALE)
    else:
        image = cv.imdecode(i, cv.IMREAD_COLOR)
    
    if(image.ndim == 3):
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    return image


def to_PIL(image_array):
    """
    Converts a NumPy image array to a PIL image.

    Args:
        image_array (np.ndarray): The image represented as a NumPy array.

    Returns:
        PIL.Image.Image: The image represented as a PIL image.
    """
    return PIL.Image.fromarray(np.uint8(image_array))


def save_image(image_array, dir_path, file_name, create_dir=True):
    """
    Saves a NumPy image array to disk.

    The image array's color channels must be ordered red, green, and blue.

    Args:
        image_array (np.ndarray): The image represented as a NumPy array.
        dir_path (str): The destination directory.
        file_name (str): The name of the image file to create.
        create_dir (bool, optional): Whether to create the destination
            directory and any missing parent directories. Defaults to
            ``True``.

    Returns:
        str: The normalized path of the created image file.
    """
    if create_dir:
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
    name = os.path.normpath(os.path.join(dir_path, file_name))
    # revert color channels from 'R','G','B' to 'B','G','R' order before saving, since opencv considers the image in 'B','G','R' order
    if image_array.ndim == 3:
        image_array = cv.cvtColor(image_array, cv.COLOR_RGB2BGR)
    cv.imwrite(filename=name, img=image_array)
    return name


def save_image_unicode(image_array, dir_path, file_name, create_dir=True):
    """
    Saves a NumPy image array to disk with Unicode path support.

    The image array's color channels must be ordered red, green, and blue.

    Args:
        image_array (np.ndarray): The image represented as a NumPy array.
        dir_path (str): The destination directory.
        file_name (str): The name of the image file to create.
        create_dir (bool, optional): Whether to create the destination
            directory and any missing parent directories. Defaults to
            ``True``.

    Returns:
        str: The normalized path of the created image file.
    """
    if create_dir:
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
    name = os.path.normpath(os.path.join(dir_path, file_name))
    # revert color channels from 'R','G','B' to 'B','G','R' order before saving, since opencv considers the image in 'B','G','R' order
    if image_array.ndim == 3:
        image_array = cv.cvtColor(image_array, cv.COLOR_RGB2BGR)
    ext = os.path.splitext(name)[1]
    result, n = cv.imencode(ext, image_array)
    if result:
        with open(name, mode='wb') as f:
            n.tofile(f)
    return name
