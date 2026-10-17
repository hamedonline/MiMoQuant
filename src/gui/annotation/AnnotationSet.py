from gui.annotation.AnnotationObjectInterface import AnnotationObjectInterface


class AnnotationSet:
    __slots__ = ['_annotation_objects', '_parent_canvas']

    def __init__(self, parent_canvas):
        self._annotation_objects = []
        self._parent_canvas = parent_canvas

    def __iter__(self):
        return iter(self._annotation_objects)

    def __len__(self):
        return len(self._annotation_objects)

    def __getitem__(self, index):
        return self._annotation_objects[index]


    def add_object(self, annotation_object: AnnotationObjectInterface):
        self._annotation_objects.append(annotation_object)

    def get_objects(self, belonging_group_label: str | None = None):
        if belonging_group_label is None:
            return self._annotation_objects
        else:
            return self.get_objects_by_group_label(belonging_group_label)

    def get_count(self, belonging_group_label: str | None = None):
        if belonging_group_label is None:
            return len(self._annotation_objects)
        else:
            return len(self.get_objects_by_group_label(belonging_group_label))

    def get_objects_by_group_label(self, belonging_group_label: str):
        return [annotation_object for annotation_object in self._annotation_objects if annotation_object.get_belonging_group_label() == belonging_group_label]

    def get_object_by_id(self, id):
        for annotation_object in self._annotation_objects:
            if annotation_object.get_id() == id:
                return annotation_object
        return None

    def remove_object_by_id(self, id):
        for annotation_object in self._annotation_objects:
            if annotation_object.get_id() == id:
                self._annotation_objects.remove(annotation_object)
                return True
        return False

    def remove_object(self, annotation_object: AnnotationObjectInterface):
        self._annotation_objects.remove(annotation_object)

    def clear(self):
        self._annotation_objects = []
