import numpy as np
import onnxruntime
# from time import time
from analyzers.AnalyzerInterface import AnalyzerInterface
from analyzers.ClassificationInfo import ClassificationInfo
from analyzers.yolox.parameters import InferenceSettings
from analyzers.yolox.utils import preprocess, postprocess, multiclass_nms
from utils.entities.data_storage import DataStorage
from cv2 import rectangle, cvtColor



class YOLOXEngine(AnalyzerInterface):
    __slots__ = [
        'storage',
    ]

    def __init__(
        self,
        classification_info: ClassificationInfo,
        inference_settings: list[InferenceSettings],
    ):
        self.storage = DataStorage()
        self._initialize_storage_items()
        self.set_analysis_parameters(
            classification_info = classification_info,
            inference_settings = inference_settings
        )

    def _initialize_storage_items(self) -> None:
        self.storage.generate_placeholders(
            keys=[
                "classification_info",  # to store classification info object
                "inference_settings",  # to store an array list of inference setting objects
                "inference_sessions",  # to store inference sessions, will be built upon initialization
                "inference_results"  # to store inference results on each inference run
            ],
            default_value={}
        )

    def _register_classification_info(self, classification_info: ClassificationInfo) -> None:
        self.storage.update({
            "classification_info": classification_info
        })

    def _register_inference_settings(self, inference_settings: list[InferenceSettings]) -> None:
        self.storage.update({
            "inference_settings": inference_settings
        })
        # register inference sessions based on the inference settings
        self._register_inference_sessions(inference_settings)

    def _register_inference_sessions(self, inference_settings: list[InferenceSettings]) -> None:
        """
        Register inference sessions based on the provided inference settings.
        final inference sessions structure:
            {
                class_id: {
                    "model_path": str,
                    "session": onnxruntime.InferenceSession,
                    "input_shape": tuple,
                    "conf_threshold": float,
                    "nms_threshold": float,
                }
                ...
            }
        """
        # clear previous sessions
        self.storage.update({
            "inference_sessions": {}
        })
        for each_setting in inference_settings:
            candidate_path = each_setting.get_model_path()
            candidate_session = None
            current_sessions = self._get_inference_sessions()
            # see if the path for model already registered
            if current_sessions is not None:
                for session_info in current_sessions.values():
                    if candidate_path == session_info.get("model_path"):
                        # if the path is already registered, use the session
                        candidate_session = session_info.get("session")
                        break
            # register the session
            self.storage.get("inference_sessions")[each_setting.class_id] = {
                "model_path": candidate_path,
                "session": onnxruntime.InferenceSession(candidate_path) if candidate_session is None else candidate_session,
                "input_shape": each_setting.get_input_shape(),
                "conf_threshold": each_setting.get_conf_threshold(),
                "nms_threshold": each_setting.get_nms_threshold()
            }

    def _get_inference_sessions(self):
        return self.storage.get("inference_sessions")

    def _get_results_storage(self):
        return self.storage.get("inference_results")
 
    def _get_classification_info(self):
        return self.storage.get("classification_info")


    def set_analysis_parameters(
        self,
        classification_info: ClassificationInfo,
        inference_settings: list[InferenceSettings]
    ) -> None:
        self._register_classification_info(classification_info)
        self._register_inference_settings(inference_settings)


    def get_conf_threshold(self, class_id: int) -> float:
        inference_settings = self.storage.get("inference_settings")
        if not inference_settings:
            raise ValueError("No inference settings registered.")

        for setting in inference_settings:
            if setting.class_id == class_id:
                return setting.get_conf_threshold()

        raise ValueError(f"No inference setting found for class_id {class_id}.")


    def update_conf_threshold(self, class_id: int, new_conf_threshold: float) -> None:
        inference_settings = self.storage.get("inference_settings")
        if not inference_settings:
            raise ValueError("No inference settings registered.")

        # find and update the InferenceSettings object for the given class_id
        for setting in inference_settings:
            if setting.class_id == class_id:
                setting.set_conf_threshold(new_conf_threshold)
                break
        else:
            raise ValueError(f"No inference setting found for class_id {class_id}.")

        # update the session info for the same class_id
        inference_sessions = self._get_inference_sessions()
        if inference_sessions is not None and class_id in inference_sessions.keys():
            inference_sessions[class_id]["conf_threshold"] = new_conf_threshold
        else:
            raise ValueError(f"No inference session found for class_id {class_id}.")


    def perform(self, image_array: np.ndarray) -> None:
        """
        Perform inference on the provided image array using the registered inference sessions.
        The results will be stored in the storage under "inference_results".
        """
        if not isinstance(image_array, np.ndarray):
            raise ValueError("Input image must be a numpy array.")

        per_class_results = {}
        for class_id, session_info in self._get_inference_sessions().items():
            session = session_info["session"]
            input_shape = session_info["input_shape"]
            conf_threshold = session_info["conf_threshold"]
            nms_threshold = session_info["nms_threshold"]

            inference_results = self.run_inference(
                session,
                image_array,
                model_input_shape=input_shape,
                conf_threshold=conf_threshold,
                nms_threshold=nms_threshold
            )
            per_class_results[class_id] = self.filter_predictions_by_class(
                inference_results,
                target_class_id=class_id,
            )

        # unify results from all classes
        unified_results = {
            "bboxes": [],
            "scores": [],
            "classes": []
        }
        for class_id, class_results in per_class_results.items():
            if class_results and len(class_results.get("bboxes", [])) > 0:
                unified_results["bboxes"].extend(class_results["bboxes"])
                unified_results["scores"].extend(class_results["scores"])
                unified_results["classes"].extend(class_results["classes"])

        # store the results
        self._update_results({
            "class_specific": per_class_results,
            "unified": unified_results
        })


    def _update_results(self, new_results: dict) -> None:
        self.storage.update({
            "inference_results": new_results
        })

    def get_results(self):
        return self._get_results_storage()

    def visualize_results(self, image_array: np.ndarray) -> np.ndarray:
        results = self.get_results()
        bboxes = results.get('unified').get('bboxes', [])
        scores = results.get('unified').get('scores', [])
        classes = results.get('unified').get('classes', [])
        if len(bboxes) == 0:
            print("No boxes detected.")
            return image_array

        image_boxed = image_array.copy()
        # iterate through each detected box tensor
        for box_id, bbox in enumerate(bboxes):
            x0 = int(bbox[0])
            y0 = int(bbox[1])
            x1 = int(bbox[2])
            y1 = int(bbox[3])

            color = self._get_classification_info().get_color_for_class(
                self._get_classification_info().get_label(int(classes[box_id])),
                scores[box_id]
            )
            image_boxed = rectangle(image_boxed, (x0, y0), (x1, y1), color=color, thickness=1)

        image_recolored = cvtColor(image_boxed, 0)
        return image_recolored


    def reset(self) -> None:
        self.storage.clear()
        self._initialize_storage_items()


    @staticmethod
    def run_inference(
        onnx_session: onnxruntime.InferenceSession,
        img_array: np.ndarray,
        model_input_shape: tuple = (320, 320),
        conf_threshold=0.4, nms_threshold=0.4,
    ) -> dict:
        img, ratio = preprocess(img_array, model_input_shape)

        # start_time = time()
        ort_inputs = {onnx_session.get_inputs()[0].name: img[None, :, :, :]}
        output = onnx_session.run(None, ort_inputs)
        output_array = np.array(output[0])
        predictions = postprocess(output_array, model_input_shape)[0]
        # end_time = time()
        # print(f"Inference time: {end_time - start_time:.3f} seconds")

        boxes = predictions[:, :4]
        scores = predictions[:, 4:5] * predictions[:, 5:]

        boxes_xyxy = np.ones_like(boxes)
        boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2]/2.
        boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3]/2.
        boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2]/2.
        boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3]/2.
        boxes_xyxy /= ratio

        dets = multiclass_nms(boxes_xyxy, scores, score_thr=conf_threshold, nms_thr=nms_threshold)
        if dets is not None:
            final_boxes, final_scores, final_cls_inds = dets[:,:4], dets[:, 4], dets[:, 5]
            return {
                "bboxes": final_boxes,
                "scores": final_scores,
                "classes": final_cls_inds
            }
        else:
            return {
                "bboxes": [],
                "scores": [],
                "classes": []
            }

    def filter_predictions_by_class(
        self,
        detection_results: dict,
        target_class_id: int | None = None,
        target_class_name: str | None = None,
        min_score: float | None = None
    ):
        """
        Filter predictions of detection results for a specific class.
        
        Args:
            detection_results (dict): Detection results containing 'bboxes', 'scores', 'classes'
            target_class_id (int, optional): Class ID to filter for (e.g., 0 for Punct, 1 for Branching)
            target_class_name (str, optional): Class name to filter for (e.g., 'Punct' or 'Branching')
            min_score (float, optional): Minimum confidence score threshold
        
        Returns:
            dict: Filtered predictions containing only the specified class (same format as input)
        """
        if not detection_results or len(detection_results.get('bboxes', [])) == 0:
            return {"bboxes": [], "scores": [], "classes": []}
        
        if target_class_id is None and target_class_name is None:
            # no class filtering, return all predictions
            return detection_results
        
        # convert class name to ID if provided
        if target_class_name is not None and target_class_id is None:
            target_class_id = self._get_classification_info().get_class_index(target_class_name)
            if target_class_id is None:
                print(f"Unknown class name: {target_class_name}")
                return {"bboxes": [], "scores": [], "classes": []}
        
        # get arrays from detection results
        bboxes = detection_results['bboxes']
        scores = detection_results['scores']
        classes = detection_results['classes']
        
        # handle case where data might be numpy arrays or lists
        if len(bboxes) == 0:
            return {"bboxes": [], "scores": [], "classes": []}
        
        bboxes = np.array(bboxes)
        scores = np.array(scores)
        classes = np.array(classes)
        
        # create filter mask
        if target_class_id is not None:
            class_mask = (classes == target_class_id)
        else:
            class_mask = np.ones(len(classes), dtype=bool)  # No class filtering
        
        # apply score threshold if provided
        if min_score is not None:
            score_mask = (scores >= min_score)
            combined_mask = class_mask & score_mask
        else:
            combined_mask = class_mask
        
        # filter predictions and maintain original format
        filtered_bboxes = bboxes[combined_mask]
        filtered_scores = scores[combined_mask]
        filtered_classes = classes[combined_mask]
        
        # return in same format as input (convert back to list if original was list)
        if isinstance(detection_results['bboxes'], list):
            return {
                "bboxes": filtered_bboxes.tolist(),
                "scores": filtered_scores.tolist(),
                "classes": filtered_classes.tolist()
            }
        else:
            return {
                "bboxes": filtered_bboxes,
                "scores": filtered_scores,
                "classes": filtered_classes
            }
