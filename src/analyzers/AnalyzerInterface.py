import numpy as np
from abc import ABC, abstractmethod



class AnalyzerInterface(ABC):
    @abstractmethod
    def set_analysis_parameters(self, params: dict) -> None:
        """Set the parameters for the analysis."""
        pass

    @abstractmethod
    def perform(self, image_array: np.ndarray) -> None:
        """Perform the analysis on the provided image array."""
        pass

    @abstractmethod
    def get_results(self) -> dict:
        """Return the results of the analysis."""
        pass

    @abstractmethod
    def visualize_results(self, image_array: np.ndarray) -> np.ndarray:
        """Visualize the results of the analysis on the provided image array."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the analyzer to its initial state."""
        pass
