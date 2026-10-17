from dataclasses import dataclass



@dataclass
class InferenceSettings:
    """
    Parameters for YOLOX inference.
    """
    class_id: int
    model_path: str
    input_shape: tuple = (320, 320)
    conf_threshold: float = 0.25
    nms_threshold: float = 0.45

    def get_class_id(self) -> int:
        return self.class_id

    def get_model_path(self) -> str:
        return self.model_path

    def get_input_shape(self) -> tuple:
        return self.input_shape

    def get_conf_threshold(self) -> float:
        return self.conf_threshold

    def get_nms_threshold(self) -> float:
        return self.nms_threshold

    def set_conf_threshold(self, conf_threshold: float) -> None:
        self.conf_threshold = conf_threshold
