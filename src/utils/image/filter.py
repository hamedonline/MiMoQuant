import cv2 as cv
import numpy as np



def clahe(
    image_array: np.ndarray,
    clip_limit: float = 40.0,
    tile_size: tuple[int, int] = (8,8)
) -> np.ndarray:
    """
    Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) on a given numpy image array.

    Args:
        image_array (np.ndarray): Image array.
        clip_limit (float, optional): Threshold for contrast limiting. Defaults to 40.0.
        tile_size (tuple[int, int], optional): Tile size for CLAHE filter. Defaults to (8,8).
    
    Returns:
        np.ndarray: Filtered image array.
    """
    clahe = cv.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    if image_array.ndim == 2:
        return clahe.apply(image_array)
    else:
        img_lab = cv.cvtColor(image_array, cv.COLOR_RGB2LAB)
        lab_planes = list(cv.split(img_lab))
        lab_planes[0] = clahe.apply(lab_planes[0])
        img_lab = cv.merge(lab_planes)
        return cv.cvtColor(img_lab, cv.COLOR_LAB2RGB)


def contrast_stretch(image_array: np.ndarray) -> np.ndarray:
    """
    Applies contrast stretch on a given numpy image array.

    Args:
        image_array (np.ndarray): Image array.
    
    Returns:
        np.ndarray: Filtered image array.
    """
    min_intensity = np.min(image_array)
    max_intensity = np.max(image_array)
    def pixel_transform(i): return ((i - min_intensity) /
                                   (max_intensity - min_intensity))*255
    transform_fn = np.vectorize(pixel_transform)
    return transform_fn(image_array).astype(np.uint8)


def histogram_equalizer(image_array: np.ndarray) -> np.ndarray:
    """
    Applies histogram equalizer on a given numpy image array.

    Args:
        image_array (np.ndarray): Image array.
    
    Returns:
        np.ndarray: Filtered image array.
    """
    if image_array.ndim == 2:
        return cv.equalizeHist(image_array)
    else:
        img_yuv = cv.cvtColor(image_array, cv.COLOR_RGB2YUV)
        # equalize the histogram of the Y channel
        img_yuv[:, :, 0] = cv.equalizeHist(img_yuv[:, :, 0])
        return cv.cvtColor(img_yuv, cv.COLOR_YUV2RGB)
