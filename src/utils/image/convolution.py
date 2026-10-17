import cv2 as cv
import numpy as np



def _check_type(type: str) -> bool:
    """
    Checks if the type is valid for convolution.

    Args:
        type (str): Convolution type. Can be either 'conv' for convolution or 'corr' for correlation.

    Returns:
        bool: True if the type is valid.

    Raises:
        ValueError: If the type is not valid.
    """
    if type not in ['conv', 'corr']:
        raise ValueError("Convolution type must be either 'conv' or 'corr'.")
    return True


def convolve2D(
    image: np.ndarray,
    kernel: np.ndarray,
    padding: int = 0,
    strides: int = 1,
    filter_type: str = 'conv'
) -> np.ndarray:
    """
    Convolve a 2D image with a kernel. This is a numpy implementation of the convolution operation.
    See the following for details:
    https://medium.com/analytics-vidhya/2d-convolution-using-python-numpy-43442ff5f381

    Args:
        image (np.ndarray): Image array.
        kernel (np.ndarray): Kernel array.
        padding (int, optional): Padding size. Defaults to 0.
        strides (int, optional): Strides size. Defaults to 1.
        filter_type (str, optional): Convolution type. Defaults to 'conv'.
            Can be either 'conv' for convolution or 'corr' for correlation.
    
    Raises:
        ValueError: If the filter type is not valid.

    Returns:
        np.ndarray: Convolved image array.
    """
    _check_type(filter_type)

    # cross correlation
    if filter_type == "conv":
        kernel = np.flip(kernel, axis=(0, 1))

    image = image / 255 # normalize the image to be in the range [0, 1]
    image_size_y, image_size_x = image.shape if image.ndim == 2 else image.shape[:2]
    kernel_size_y, kernel_size_x = kernel.shape if kernel.ndim == 2 else kernel.shape[:2]

    # shape of output result
    output_size_x = int(((image_size_x - kernel_size_x + 2 * padding) / strides) + 1)
    output_size_y = int(((image_size_y - kernel_size_y + 2 * padding) / strides) + 1)
    output_img = np.zeros((output_size_y, output_size_x))

    # apply equal padding to all sides
    if padding != 0:
        image_padded = np.zeros((image_size_y + padding*2, image_size_x + padding*2))
        image_padded[int(padding):int(-1 * padding), int(padding):int(-1 * padding)] = image
    else:
        image_padded = image

    # iterate convolution through image
    for y in range(image_size_y):
        # exit convolution when y has moved out of the image
        if y > image_size_y - kernel_size_y:
            break
        # only convolve if y has gone down by the specified strides
        if y % strides == 0:
            for x in range(image_size_x):
                # go to next row once kernel is out of bounds
                if x > image_size_x - kernel_size_x:
                    break
                try:
                    # only convolve if x has moved by the specified strides
                    if x % strides == 0:
                        # output_img[y, x] = (kernel * image_padded[y: y + kernel_size_y, x: x + kernel_size_x]).sum()
                        output_img[y, x] = (np.multiply(kernel, image_padded[y: y + kernel_size_y, x: x + kernel_size_x])).sum()
                except Exception as e:
                    print(e)
                    break

    ## normalize the output image to be in the range [0, 255], zero out negative values, and convert to int
    # output_img *= (255.0/output_img.max())
    ## normalize into the range [0, 255]
    # output_img = ((output_img - np.min(output_img)) / (np.max(output_img) - np.min(output_img)) * 255)
    # output_img = np.where(output_img < 0, 0, output_img).astype(np.int8)
    # output_img *= (1.0/output_img.max())
    # output_img = (output_img - np.min(output_img)) / (np.max(output_img) - np.min(output_img))
    # output_img *= 255.0
    output_scaled = (output_img - output_img.min()) / (output_img.max() - output_img.min())
    output_result = (output_scaled * 255).astype("uint8")
    return output_result


def convolve2D_opencv(
    image: np.ndarray,
    kernel: np.ndarray,
    filter_type: str = 'conv',
    border_type: int = cv.BORDER_CONSTANT
) -> np.ndarray:
    """
    Filter an image with a kernel.

    Args:
        image_array (np.ndarray): Image array.
        kernel_array (np.ndarray): Kernel array.
        filter_type (str, optional): Filter type. Defaults to 'conv'.
            Can be either 'conv' for convolution or 'corr' for correlation.
        border_type (int, optional): Border type. Defaults to cv.BORDER_CONSTANT.
            A flag that specifies what kind of border to be added to the surrounding of the image.
            Some common border types include:
                cv.BORDER_CONSTANT - Adds a constant colored border.
                cv.BORDER_REFLECT - Border will be mirror reflection of the border elements.
                cv.BORDER_REPLICATE - Border will replicate the last element.
                cv.BORDER_WRAP - Border will be a copy of the opposite edge of the image.

    Raises:
        ValueError: Filter type must be either 'conv' or 'corr'.

    Returns:
        np.ndarray: Filtered image array.
    """
    _check_type(filter_type)

    if filter_type == "conv":
        kernel = cv.flip(kernel, -1)

    return cv.filter2D(src=image, ddepth=-1, kernel=kernel, borderType=border_type)


def convolve2D_custom(
        image: np.ndarray,
        kernel: np.ndarray,
    ):
    """
    Applies a two-dimensional convolution to an image.

    Implementation based on:
    https://github.com/Lew-Morris/filter2D

    Args:
        image (np.ndarray): The input image.
        kernel (np.ndarray): The filter kernel to apply.

    Returns:
        np.ndarray: The resulting convolved image.
    """
    # get size of kernel
    m = kernel.shape[0]
    n = kernel.shape[1]

    # pad image with 1px of 0's on each side
    input_image = cv.copyMakeBorder(image, 1, 1, 1, 1, cv.BORDER_CONSTANT, value=(0, 0, 0))

    # store size of image minus the padding
    dim_y = input_image.shape[0] - m + 1
    dim_x = input_image.shape[1] - n + 1

    # create a new, zeroed array (image)
    new_image = np.zeros((dim_y, dim_x))

    # loop through each pixel and apply the filter
    for i in range(dim_y):
        for j in range(dim_x):
            # take the sum of each pixel and then multiply by the kernel (filter)
            conv = (np.sum(input_image[i:i + m, j:j + n] * kernel))

            # threshold image to prevent clipping
            if conv < 0:
                new_image[i][j] = 0
            elif conv > 255:
                new_image[i][j] = 255
            else:
                new_image[i][j] = conv
    return new_image
