import os
import shutil
from typing import Literal
from utils.general import is_empty, remove_duplicates
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"



def extract_filenames(
        dir_path: str,
        include_subfolders: bool = True,
        file_extension: str | list[str] | None = None,
        filter_by_name: bool = False,
        filter_value: str = '',
        filter_mode: Literal['include', 'exclude'] = 'include'
    ) -> list[dict]:
    """
    Extracts file information for files in a directory.

    Args:
        dir_path (str): The directory path containing the files.
        include_subfolders (bool, optional): Whether to search inside
            subfolders. Defaults to ``True``.
        file_extension (str | list[str] | None, optional): The desired file
            suffix or suffixes. If ``None``, files with any suffix are
            returned. Defaults to ``None``.
        filter_by_name (bool, optional): Whether to filter files by name.
            Defaults to ``False``.
        filter_value (str, optional): The string to search for in file names.
            Defaults to ``''``.
        filter_mode (Literal['include', 'exclude'], optional): Whether to
            include or exclude files containing ``filter_value``. Defaults to
            ``'include'``.

    Returns:
        list[dict]: A list of file-information dictionaries containing each
        file's name, raw name, suffix, path, directory, and size.

    Raises:
        TypeError: If ``file_extension`` is neither a string nor a list of
            strings.
    """
    # evaluate file extension
    if file_extension is None or is_empty(file_extension): # if Nonetype or an empty list
        file_extension = ['']
    elif isinstance(file_extension, str):
        file_extension = [file_extension]
    elif isinstance(file_extension, list):
        for suffix in file_extension:
            if not isinstance(suffix, str):
                raise TypeError("File extension must be either a string or a list of string type.")
    else:
        raise TypeError("File extension must be either a string or a list of string type.")

    # replace backslashes with forward slashes to avoid path issues
    dir_path = dir_path.replace('\\\\', '/').replace('\\', '/')

    # add dot to suffix if it is missing
    for id, suffix in enumerate(file_extension):
        if not suffix.startswith('.'):
            file_extension[id] = '.'+ file_extension[id]

    name_list = []

    if include_subfolders:
        for path, subdirs, files in os.walk(dir_path):
            for name in files:
                file_is_approved = False
                file_suffix = os.path.splitext(name)[-1]
                for desired_suffix in file_extension:
                    if len(desired_suffix) > 1:
                        if file_suffix == desired_suffix:
                            if filter_by_name:
                                if filter_mode == 'include':
                                    if filter_value in os.path.splitext(name)[0]:
                                        file_is_approved = True
                                else:
                                    if filter_value not in os.path.splitext(name)[0]:
                                        file_is_approved = True
                            else:
                                file_is_approved = True
                    else:
                        if filter_by_name:
                            if filter_mode == 'include':
                                if filter_value in os.path.splitext(name)[0]:
                                    file_is_approved = True
                            else:
                                if filter_value not in os.path.splitext(name)[0]:
                                    file_is_approved = True
                        else:
                            file_is_approved = True

                if file_is_approved:
                    name_list.append(generate_file_info(file_path=path, file_name=name))

    else:
        for name in os.listdir(dir_path):
            path = os.path.join(dir_path, name)
            if os.path.isdir(path):
                continue # skip directories

            file_is_approved = False
            file_suffix = os.path.splitext(name)[-1]
            for desired_suffix in file_extension:
                if len(desired_suffix) > 1:
                    if file_suffix == desired_suffix:
                        if filter_by_name:
                            if filter_mode == 'include':
                                if filter_value in os.path.splitext(name)[0]:
                                    file_is_approved = True
                            else:
                                if filter_value not in os.path.splitext(name)[0]:
                                    file_is_approved = True
                        else:
                            file_is_approved = True
                else:
                    if filter_by_name:
                        if filter_mode == 'include':
                            if filter_value in os.path.splitext(name)[0]:
                                file_is_approved = True
                        else:
                            if filter_value not in os.path.splitext(name)[0]:
                                file_is_approved = True
                    else:
                        file_is_approved = True

            if file_is_approved:
                name_list.append(generate_file_info(file_path=dir_path, file_name=name))

    # checking and removing for duplicates is necessary, since it is mistakenly possible to provide for example both ['', '.suffix'] as file_extension argument
    return remove_duplicates(name_list)


def generate_file_info(file_path: str, file_name: str = "") -> dict:
    """
    Generates information about a file.

    Args:
        file_path (str): The file path, or the directory containing the file.
        file_name (str, optional): The file name. If omitted, ``file_path`` is
            treated as the complete file path. Defaults to ``""``.

    Returns:
        dict: A dictionary containing the file's ``name``, ``name_raw``,
        ``suffix``, absolute ``path``, ``file_dir``, and ``file_size``.

    Raises:
        ValueError: If ``file_path`` is not a valid complete file path when
            ``file_name`` is omitted.
    """
    info_dic = {}

    # in case file_name is None, we have to make sure the provided file_path is the complete path, ending with a file name plus its suffix (extension)
    if len(file_name) == 0 and not is_valid_file_path(file_path):
        raise ValueError("The provided file_path is not a valid file path.")

    if len(file_name) == 0:  # extract the file_name from the file_path, since it is not provided explicitly
        file_name = os.path.basename(file_path)
        abs_path = file_path
    else:
        abs_path = os.path.join(file_path, file_name)
    abs_path = os.path.normpath(abs_path)
    file_name_raw, file_extension = os.path.splitext(file_name)
    file_dir = os.path.dirname(abs_path)
    file_size = os.path.getsize(abs_path) if file_exists(abs_path) else None

    info_dic['name'] = file_name
    info_dic['name_raw'] = file_name_raw
    info_dic['suffix'] = file_extension
    info_dic['path'] = abs_path
    info_dic['file_dir'] = file_dir
    info_dic['file_size'] = file_size

    return info_dic


def is_valid_file_path(file_path: str) -> bool:
    """
    Checks whether the provided file path is valid.

    Args:
        file_path (str): The complete path to the file.

    Returns:
        bool: ``True`` if the file path is valid; otherwise, ``False``.
    """
    # check if the input is a non-empty string
    if not isinstance(file_path, str) or not file_path.strip():
        return False

    # check if the path contains at least one directory separator
    if os.path.sep not in file_path and (os.path.altsep is None or os.path.altsep not in file_path):
        return False

    # extract the file name from the path
    file_name = os.path.basename(file_path)

    # check if the filename is empty
    if not file_name:
        return False

    # check if there is a dot in the file name indicating an extension
    if '.' not in file_name:
        return False

    # split the file name into name and extension
    name, ext = os.path.splitext(file_name)
    # check that the name is non-empty and extension is not a single dot
    if not name or len(ext) == 1:
        return False

    return True


def file_exists(file_path: str) -> bool:
    """
    Checks whether a file exists at the provided path.

    Args:
        file_path (str): The complete path to the file.

    Returns:
        bool: ``True`` if the file exists; otherwise, ``False``.
    """
    return os.path.isfile(file_path)


def copy_file(src_path, dst_path, create_dir=True):
    """
    Copies the source file to the destination.

    Args:
        src_path (str): The complete path to the source file.
        dst_path (str): The complete destination path, including the file name.
        create_dir (bool, optional): Whether to create the destination
            directory if it does not exist. Defaults to ``True``.

    Returns:
        str: The path of the copied file, or ``None`` if copying fails.
    """
    try:
        return shutil.copy(src_path, dst_path)
    except IOError as io_err:
        if create_dir:
            try:
                os.makedirs(os.path.dirname(dst_path))
                return shutil.copy(src_path, dst_path)
            except IOError as io_err_inner:
                print(io_err_inner)
        print(io_err)


def move_file(src_path, dst_path, create_dir=True):
    """
    Moves the source file to the destination.

    Args:
        src_path (str): The complete path to the source file.
        dst_path (str): The complete destination path, including the file name.
        create_dir (bool, optional): Whether to create the destination
            directory if it does not exist. Defaults to ``True``.

    Returns:
        str: The path of the moved file, or ``None`` if moving fails.
    """
    try:
        return shutil.move(src_path, dst_path)
    except IOError as io_err:
        if create_dir:
            try:
                os.makedirs(os.path.dirname(dst_path))
                return shutil.move(src_path, dst_path)
            except IOError as io_err_inner:
                print(io_err_inner)
        print(io_err)
