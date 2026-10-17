import pickle
import numpy as np
from time import localtime, strftime
from os import path, makedirs
from subprocess import Popen
from tkinter import filedialog
from pandas import ExcelWriter, DataFrame
from managers.Manager import Manager
from managers.Coordinator import Coordinator
from utils.image.io import save_image_unicode
from utils.general import generate_random_unique_string



class FileManager(Manager):
    __slots__ = [
        'coordinator',
        'state_manager',
        'display_manager',
        'identifier_for_cutouts',
        'default_img_save_extension_cutout',
        'default_img_save_extension_annotation',
    ]

    # ************************************************
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__()
        self.coordinator = coordinator
        self.identifier_for_cutouts = "_cutout"
        self.default_img_save_extension_cutout = "png"
        self.default_img_save_extension_annotation = "jpg"

    def assign_comanagers(self):
        self.state_manager = self.coordinator.ask_for_manager('state')
        self.display_manager = self.coordinator.ask_for_manager('display')

    def perform_post_init_tasks(self):
        self.assign_comanagers()


    # ************************************************
    def _get_file_types(self):
        if self.get_default_save_extension_cutout() == "png":
            return [("PNG files", "*.png"), ("JPG files", "*.jpg")]
        else:
            return [("JPG files", "*.jpg"), ("PNG files", "*.png")]


    def _next_identifier_counter(self, file_path_pattern: str):
        # https://stackoverflow.com/a/47087513
        i = 1

        # first do an exponential search
        while self.file_exists(file_path_pattern.format(i)):
            i = i * 2

        # result lies somewhere in the interval (i/2..i]
        # we call this interval (a..b] and narrow it down until a + 1 = b
        a, b = (i // 2, i)
        while a + 1 < b:
            c = (a + b) // 2  # interval midpoint
            a, b = (c, b) if self.file_exists(file_path_pattern.format(c)) else (a, c)

        return b


    @staticmethod
    def generate_unique_filename(
        prefix: str = "",
        use_current_time: bool = True,
        use_random_string: bool = True,
        random_string_length: int = 4,
        separator: str = "_",
    ) -> str:
        """
        Generate a unique file name with optional prefix, timestamp, and random string.

        This method creates a unique identifier by combining an optional prefix with a timestamp
        and/or a random string. At least one of timestamp or random string must be used.

        Args:
            prefix (str, optional): A string to prepend to the unique name. Defaults to "".
            use_current_time (bool, optional): Whether to include a timestamp in the format
                YYYYMMDD-HHMMSS. Defaults to True.
            use_random_string (bool, optional): Whether to include a random string. Defaults to True.
            random_string_length (int, optional): The length of the random string. Defaults to 4.

        Returns:
            str: A unique string in the format "{prefix}_{timestamp}_{random_string}".

        Raises:
            ValueError: If both use_current_time and use_random_string are False.

        Examples:
            >>> generate_unique_file_name("test")
            'test_20230615-123045_a7f3'
            >>> generate_unique_file_name(use_current_time=False)
            '_b4e9'
        """
        if not use_current_time and not use_random_string:
            raise ValueError("Either use_current_time or use_random_string must be True.")
        current_time = strftime("%Y%m%d-%H%M%S", localtime()) if use_current_time else "" # format: YYYYMMDD-HHMMSS
        random_string = generate_random_unique_string(random_string_length) if use_random_string else ""
        combined_string_list = [prefix, current_time, random_string]
        combined_unique_string = separator.join(filter(None, combined_string_list))
        return combined_unique_string


    def get_identifier_for_cutout_images(self):
        return self.identifier_for_cutouts


    def get_default_save_extension_cutout(self):
        return self.default_img_save_extension_cutout


    def set_default_save_extension_cutout(self, extension: str):
        self.default_img_save_extension_cutout = extension


    def get_default_save_extension_annotation(self):
        return self.default_img_save_extension_annotation


    def set_default_save_extension_annotation(self, extension: str):
        self.default_img_save_extension_annotation = extension


    @staticmethod
    def dir_exists(dir_path):
        return True if path.isdir(dir_path) else False


    @staticmethod
    def file_exists(file_path):
        return True if path.exists(file_path) else False


    @staticmethod
    def create_dir(dir_path):
        if not FileManager.dir_exists(dir_path):
            makedirs(dir_path)


    @staticmethod
    def read_object(obj_path):
        """
        Reads a Python object from disk.

        Args:
            obj_path (str): The complete path to the object file.

        Returns:
            Any: The loaded Python object, or ``None`` if reading fails.
        """
        try:
            with open(file=obj_path, mode='rb') as input:
                return pickle.load(input)
        except Exception as e:
            print(f"Error reading object: {e}")
            return None


    @staticmethod
    def save_object(obj, dir_path, file_name, file_extension='pkl', create_dir=True):
        """
        Saves a Python object to disk.

        Args:
            obj (Any): The Python object to save.
            dir_path (str): The destination directory.
            file_name (str): The base name of the object file.
            file_extension (str, optional): The file extension. A leading dot
                is removed if provided. Defaults to ``'pkl'``.
            create_dir (bool, optional): Whether to create the destination
                directory if it does not exist. Defaults to ``True``.

        Returns:
            str: The path of the created object file, or ``None`` if saving
            fails.
        """
        # if there is a dot in the file extension, remove it
        if '.' in file_extension:
            file_extension = file_extension.split('.')[-1]
        try:
            if create_dir:
                FileManager.create_dir(dir_path)
            name = path.normpath(path.join(dir_path, file_name+'.'+file_extension))
            with open(name, 'wb') as output:  # overwrites any existing file
                pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
                return name
        except Exception as e:
            print(f"Error saving object: {e}")
            return None



    def suggest_file_name(
        self,
        save_dir: str,
        base_name: str, # base file name, example: "image.jpg"
        additional_prefix: str = "", # prefix to be added to the base name, before number addition, example: "_cutout_" => image_cutout_1.jpg
        additional_postfix: str = "", # postfix to be added after number addition, example: "_processed" => image_cutout_1_processed.jpg
    ) -> str:
        file_name_raw = base_name.rsplit(".", 1)[0]
        name_pattern = file_name_raw + additional_prefix + "_{:d}" + "." + self.get_default_save_extension_cutout()
        path_pattern = save_dir + "/" + name_pattern
        formatted_name = name_pattern.format(self._next_identifier_counter(path_pattern))
        final_name = formatted_name.rsplit(".", 1)
        suggestion_name = final_name[0] + additional_postfix + "." + final_name[1]
        return suggestion_name


    def save_image_via_array(
        self,
        image_array: np.ndarray,
        save_dir: str,
        file_name: str,
    ):
        try:
            save_image_unicode(
                image_array = image_array,
                dir_path = save_dir,
                file_name = file_name,
            )
        except Exception as e:
            print(f"Error saving image: {e}")


    def save_image_via_dialog(
        self,
        image_array: np.ndarray,
        window_title: str,
        save_dir: str,
        file_name: str,
        additional_prefix: str = "",
        additional_postfix: str = "",
    ):
        try:
            suggested_name: str
            if self.state_manager.is_roi_from_file():
                suggested_name = self.display_manager.get_roi_image().get_file_name()
            else:
                suggested_name = self.suggest_file_name(
                    save_dir,
                    file_name,
                    additional_prefix,
                    additional_postfix,
                )
            save_path = filedialog.asksaveasfilename(
                title = window_title,
                filetypes = self._get_file_types(),
                confirmoverwrite = True,
                initialdir = save_dir,
                initialfile = suggested_name,
                defaultextension = "." + self.get_default_save_extension_cutout(),
            )
            if save_path:
                self.save_image_via_array(
                    image_array = image_array,
                    save_dir = save_path.rsplit("/", 1)[0],
                    file_name = save_path.rsplit("/", 1)[1],
                )
                # save_image_unicode(
                #     image_array = image_array,
                #     dir_path = save_path.rsplit("/", 1)[0],
                #     file_name = save_path.rsplit("/", 1)[1],
                # )
                self.set_default_save_extension_cutout(save_path.rsplit(".", 1)[1])
                return save_path
            return None
        except Exception as e:
            print(f"Error saving image: {e}")


    def save_spreadsheet(self, df: DataFrame, path_to_save: str, sheet_name: str = "Sheet1"):
        with ExcelWriter(path=path_to_save, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]

            # adjust column widths based on content
            column_widths = {col: max(df[col].astype(str).map(len).max(), len(col)) + 2 for col in df.columns}
            for col_num, (col_name, width) in enumerate(column_widths.items()):
                worksheet.set_column(col_num, col_num, width)

            # adjust zoom level
            worksheet.set_zoom(90)
            print(f"DataFrame successfully exported to {path_to_save}")


    def save_excel_via_dialog(
        self,
        data_frame: DataFrame,
        window_title: str,
        file_name: str,
        sheet_name: str = "Sheet1",
        initial_dir: str | None = None,
    ):
        try:
            save_path = filedialog.asksaveasfilename(
                title=window_title,
                filetypes=[("Excel Workbook", "*.xlsx")],
                confirmoverwrite=True,
                initialdir=initial_dir,
                initialfile=file_name,
                defaultextension=".xlsx",
            )
            if save_path:
                self.save_spreadsheet(
                    df=data_frame,
                    path_to_save=save_path,
                    sheet_name=sheet_name,
                )
                return save_path
            return None
        except Exception as e:
            print(f"Error saving spreadshit: {e}")


    def select_directory_via_dialog(self, window_title: str | None = None, initial_dir: str | None = None) -> str | None:
        """Opens a dialog box to select a directory.
        Args:
            window_title (str): The title of the dialog box window.
            initial_dir (str): The initial directory to be displayed in the dialog box.
        Returns:
            str: The selected directory path.
        """
        try:
            return filedialog.askdirectory(
                title = window_title,
                initialdir = initial_dir,
            )
        except Exception as e:
            print(f"Error selecting directory: {e}")
            return None


    def launch_from_path(self, target_path: str):
        """Launches (opens) a file or directory using the default system application.
        Args:
            target_path (str): The path to the file or directory to be opened
        Raises:
            ValueError: If the operating system is not supported
            Exception: Any exception that may occur during the opening process
        """
        try:
            if self.coordinator.os_is_windows():
                from os import startfile
                startfile(target_path)
            elif self.coordinator.os_is_linux():
                # system(f'xdg-open "{path}"')
                Popen(["xdg-open", target_path])
            elif self.coordinator.os_is_mac():
                # system(f'open "{path}"')
                Popen(["open", target_path])
            else:
                raise ValueError("Unsupported operating system.")
        except Exception as e:
            print(f"Error opening directory: {e}")
