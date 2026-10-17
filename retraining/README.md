# Retraining the Analysis Model for MiMoQuant

## Overview

The MiMoQuant software uses a deep learning model for object detection and quantification of Puncta and Branching points in 2D microscopy images. While the pre-trained model is effective for some cell lines, you may want to retrain or fine-tune the model using your own annotated images to improve performance on specific cell line data.

---

## 🗃️ Data Preparation

If you have annotated new images using MiMoQuant, the annotations are saved as metadata files. Before you can train or refine the model, these must be converted to the standard COCO bounding box format.

The notebook scripts in this folder will provide the conversion steps you need to prepare your dataset for training.

NOTE: The clean conversion scripts are under development and will be provided shortly in an update.

---

## Model Training

MiMoQuant uses the [YOLOX](https://github.com/Megvii-BaseDetection/YOLOX) architecture for object detection. We chose YOLOX-m (medium) for a balance between accuracy and computational efficiency.

You can refer to the YOLOX documentation for detailed information on training and fine-tuning the model [in the official repository](https://github.com/Megvii-BaseDetection/YOLOX/blob/main/docs/train_custom_data.md).

Pretrained weights for the YOLOX-m that were used to train the MiMoQuant analysis model are available in the `pretrained_weights/` directory. You may as well use these weights as a starting point for transfer learning or fine-tuning on your own dataset.

There is an example configuration file `yolox_m_mimoquant.py` in the `pretrained_weights/` directory that specifies the model architecture, dataset paths, and training parameters. You need to modify this file to suit your dataset path and training requirements. The defaults in this file are what we used to train the MiMoQuant analysis model.

After the training process, the best model weights will be saved in the `YOLOX_outputs/` directory of the YOLOX train base folder. You will need to convert this weights file to onnxruntime format for inference in MiMoQuant.

Add the required dependencies for onnxruntime depending on your virtual environment:

```bash
> uv add onnx onnxscript onnxruntime onnxsim

OR

> pip install --upgrade onnx onnxscript onnxruntime onnxsim
```

To convert the trained weights to onnx Navigate to the YOLOX base folder with activated virtual environment and run the following command:

```bash
> python tools/export_onnx.py -n yolox-m --opset 18 --output-name inference/sample_inference.onnx -f exps/yolox_m_mimoquant.py -c YOLOX_outputs/best_ckpt.pth
```
