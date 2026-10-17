import typing
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MaxNLocator



def normalize_kernel(kernel_array: np.ndarray):
    """
    Normalizes the kernel array so that the sum of all elements is 1.

    Args:
        kernel_array (np.ndarray): The kernel array to normalize.

    Returns:
        np.ndarray: The normalized kernel array.
    """
    kernel_sum = np.sum(kernel_array)
    max_val = np.max(kernel_array)
    if kernel_sum != 0:
        # return kernel_array / kernel_sum
        return kernel_array / max_val
    return kernel_array


def amplify_negative_values(kernel: np.ndarray, amp_factor: float) -> np.ndarray:
    """
    Amplifies negative values of a kernel by a given factor.
    Args:
        kernel (np.ndarray): kernel array.
        amp_factor (float): factor to amplify negative values by.
    Returns:
        np.ndarray: amplified kernel array.
    """
    # create multiplication matrix which contains factor elements for each negative value of kernel array
    mul_matrix = (kernel < 0).astype(int) * amp_factor
    # replace zero values of multiplication matrix with ones
    mul_matrix[mul_matrix == 0] = 1
    # return value-wise multiplication of kernel and multiplication matrix as the result
    return np.multiply(kernel, mul_matrix)


def plot_kernel_in_2D(kernel: np.ndarray, title: str = "2D Kernel", cmap: str | None = None):
    """
    Plots the given kernel array on a 2D grid.

    Args:
        kernel (np.ndarray): The kernel array to plot.
        title (str): The title of the plot.
        cmap (str): The color map to use for the plot.
    """
    kernel_size_y, kernel_size_x = kernel.shape

    plt.imshow(kernel, origin='lower', interpolation='none', cmap=cmap)
    plt.title(title)
    plt.xlabel('x [pixels]')
    plt.ylabel('y [pixels]')
    plt.xticks(np.arange(0, kernel_size_x, 2))
    plt.yticks(np.arange(0, kernel_size_y, 2))
    plt.colorbar()
    plt.show()


def plot_kernel_in_3D(
    kernel: np.ndarray,
    title: str = "3D Kernel",
    fig_size: tuple[int, int] = (10,10),
    view_init: tuple[int, int] = (0, 30),
    cmap: str | None = None
) -> None:
    """
    Plots the given kernel array as a 3D surface plot.

    Args:
        kernel (np.ndarray): The kernel array to plot.
        title (str): The title of the plot.
        fig_size (tuple[int, int]): The size of the figure.
        view_init (tuple[int, int]): The initial view of the 3D plot. The first value is the elevation and the second value is the azimuth.
        cmap (str): The color map to use for the plot.

    Returns:
        None
    """
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_subplot(111, projection=Axes3D.name)
    ax = typing.cast(Axes3D, ax)

    kernel_size_y, kernel_size_x = kernel.shape

    x = np.arange(0, kernel_size_x, 1)
    y = np.arange(0, kernel_size_y, 1)
    X, Y = np.meshgrid(x, y)
    Z = kernel

    ax.plot_surface(X, Y, Z, cmap=cmap)
    ax.set_title(title)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    elev, azim = view_init
    Axes3D.view_init(ax, elev, azim)

    plt.show()
