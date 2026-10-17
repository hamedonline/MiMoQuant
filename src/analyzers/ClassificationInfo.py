from dataclasses import dataclass, field


@dataclass
class ClassificationInfo:
    label_to_index: dict[str, int]
    index_to_label: dict[int, str] = field(init=False)
    color_profiles: dict[str, dict[str, tuple[int, int, int]]] = field(default_factory=dict)
    # color profiles example:
    # {
    #     "class_1": {
    #         "low": (255, 180, 180),  # light red
    #         "medium": (255, 120, 120),  # medium red
    #         "high": (255, 0, 0)  # red
    #     },
    #     "class_2": {
    #         "low": (180, 180, 255),  # light blue
    #         "medium": (120, 120, 255),  # medium blue
    #         "high": (0, 0, 255)  # blue
    #     }
    # }
    threshold_levels: dict[str, float] = field(
        default_factory=lambda: {"low": 0.2, "medium": 0.5, "high": 0.8}
    )

    def __post_init__(self):
        self.index_to_label = {v: k for k, v in self.label_to_index.items()}
        self.num_classes = len(self.label_to_index)
        if not self.color_profiles:
            self.color_profiles = self._generate_default_color_profiles()
        self._check_if_inputs_are_valid()


    def _generate_default_color_profiles(self) -> dict[str, dict[str, tuple[int, int, int]]]:
        # return {
        #     label: {
        #         "low": (255, 180, 180),  # light red
        #         "medium": (255, 120, 120),  # medium red
        #         "high": (255, 0, 0)  # red
        #     } for label in self.label_to_index.keys()
        # }
        sorted_levels = [lvl for lvl, _ in sorted(self.threshold_levels.items(), key=lambda kv: kv[1], reverse=True)]
        n = len(sorted_levels)
        # bright/pale endpoints
        min_val = 0 # for bright spectrum
        max_val = 180 # for pale spectrum

        color_profiles: dict[str, dict[str, tuple[int, int, int]]] = {}
        for label in self.label_to_index:
            lvl_map: dict[str, tuple[int, int, int]] = {}
            for i, lvl in enumerate(sorted_levels):
                if n == 1:
                    v = min_val
                else:
                    # linear interpolation: i=0 → max_val, i=n-1 → min_val
                    v = max_val - int((max_val - min_val) * (i/(n-1)))
                lvl_map[lvl] = (255, v, v)
            color_profiles[label] = lvl_map

        return color_profiles


    def _check_if_inputs_are_valid(self) -> None:
        # threshold_levels should be between 0 and 1
        for level, value in self.threshold_levels.items():
            if not (0 <= value <= 1):
                raise ValueError(f"Threshold level '{level}' must be between 0 and 1, got {value}.")

        # color_profiles must cover exactly the same class labels (each class label must have a color profile defined)
        classes_set = set(self.label_to_index)
        colors_set = set(self.color_profiles)
        missing = classes_set - colors_set
        extra = colors_set - classes_set
        if missing or extra:
            parts = []
            if missing:
                parts.append(f"missing profiles for: {missing}")
            if extra:
                parts.append(f"unknown profiles for: {extra}")
            raise ValueError("Color‐profile keys mismatch: " + "; ".join(parts))

        # each color profile must have exactly the same threshold‐levels
        threshold_levels_set = set(self.threshold_levels.keys())
        for label, color_profile in self.color_profiles.items():
            if set(color_profile.keys()) != threshold_levels_set:
                raise ValueError(f"Color profile for class '{label}' must have the same threshold levels as defined: {threshold_levels_set}")


    def get_label(self, class_index: int) -> str:
        try:
            return self.index_to_label[class_index]
        except KeyError:
            raise ValueError(f"Class index '{class_index}' not found.")


    def get_class_index(self, label: str) -> int:
        try:
            return self.label_to_index[label]
        except KeyError:
            raise ValueError(f"Label '{label}' not found.")


    def get_class_count(self) -> int:
        return self.num_classes


    def get_color_profile(self, label: str) -> dict[str, tuple[int, int, int]]:
        try:
            return self.color_profiles[label]
        except KeyError:
            raise ValueError(f"Color profile for label '{label}' not found.")


    def get_color_for_class(self, label: str, score: float) -> tuple[int, int, int]:
        """
        Get color based on class name and score dynamically.
        """
        if label not in self.color_profiles:
            return (255, 255, 255)  # default to white if class not found

        # get sorted threshold levels (ascending order)
        sorted_thresholds = sorted(self.threshold_levels.items(), key=lambda x: x[1])

        # find the appropriate threshold level based on score
        selected_level = None
        for level_name, threshold_value in sorted_thresholds:
            if score >= threshold_value:
                selected_level = level_name
            else:
                break

        # if score is below all thresholds, use the lowest level
        if selected_level is None:
            selected_level = sorted_thresholds[0][0]

        return self.color_profiles[label][selected_level]
