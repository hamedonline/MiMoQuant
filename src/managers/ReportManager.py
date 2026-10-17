import pandas as pd
from managers.Manager import Manager
from managers.Coordinator import Coordinator
from managers.FileManager import FileManager
from utils.file.io import extract_filenames
from gui.annotation.AnnotationCircle import AnnotationCircle
from gui.annotation.AnnotationCrossMark import AnnotationCrossMark


class ReportManager(Manager):
    __slots__ = [
        'coordinator',
        'file_manager',
        'annotations_report_filename',
    ]
    ANNOTATIONS_REPORT_FILENAME = "Annotation Report"


    # ************************************************
    def __init__(self, coordinator: Coordinator) -> None:
        super().__init__()
        self.coordinator = coordinator

    def assign_comanagers(self):
        self.file_manager = self.coordinator.ask_for_manager('file')

    def perform_post_init_tasks(self):
        self.assign_comanagers()


    # ************************************************
    @classmethod
    def get_annotations_report_filename(cls):
        return cls.ANNOTATIONS_REPORT_FILENAME

    @classmethod
    def generate_unique_annotations_report_filename(cls):
        return FileManager.generate_unique_filename(
            prefix=ReportManager.get_annotations_report_filename(),
        )


    # ************************************************
    def get_count_of_specific_annotations(self, annotation_list):
        """
        Count occurrences of each 'type' in a list of annotation dictionaries.

        Args:
            annotation_list: List of annotation dictionaries with 'type' key

        Returns:
            Dictionary with types as keys and their counts as values
        """
        type_counts = {}

        for annotation in annotation_list:
            annotation_type = annotation.get('type')
            if annotation_type:
                type_counts[annotation_type] = type_counts.get(annotation_type, 0) + 1

        return type_counts


    def generate_spreadsheet_df(self, path_to_explore: str):
        print("Generating spreadsheet dataframe...")

        stats_column_labels = {
            AnnotationCircle.get_name_label(): self.coordinator.get_global_label_of_the_puncts(),
            AnnotationCrossMark.get_name_label(): self.coordinator.get_global_label_of_the_branchings()
        }

        metadata_files = extract_filenames(
            dir_path=path_to_explore,
            include_subfolders=True,
            file_extension=self.coordinator.get_global_annotation_metadata_file_extension(),
        )

        data_rows = []
        for file in metadata_files:
            # to do: if the corresponding png file exists with the same name

            file_content = self.file_manager.read_object(file['path'])
            if file_content is None:
                continue

            data_row_dict = {
                "File Name": f"{file['name_raw']}",
                "Folder Path": file['file_dir'],
            }

            counts = self.get_count_of_specific_annotations(file_content['annotations'])
            for column_name, label in stats_column_labels.items():
                data_row_dict[f"Number of {label}"] = counts.get(column_name, 0)
            data_row_dict['Total Annotations'] = sum(counts.values())

            data_rows.append(data_row_dict)

        df = pd.DataFrame(data_rows)
        print("Spreadsheet dataframe generated successfully.")
        return df
