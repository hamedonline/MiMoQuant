# MiMoQuant

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/hamedonline/MiMoQuant)](https://github.com/hamedonline/MiMoQuant/releases)

MiMoQuant is an open-source tool designed for rapid annotation and quantification of fragments and branching points in mitochondrial image analysis.

For end-users, we provide ready-to-use compiled binaries. For researchers and developers, we provide source code and the full data preparation and model refinement pipeline, alongside the dataset used for training and evaluation.

---

## 📑 Table of Contents

1. [Download & Installation (Binaries)](#-download--installation-binaries)
2. [Development & Running from Source](#-development-and-running-from-source)
3. [Building from Source](#-building-from-source)
4. [Running the Main Program](#️-running-the-main-program)
5. [Dataset and Sample Images](#️-dataset-and-sample-images)
6. [Model Retraining](#-model-retraining)
7. [Citation](#-citation)
8. [License & Acknowledgements](#-license--acknowledgements)

---

## 🚀 Download & Installation (Binaries)

If you only want to use the software without modifying the source code or retraining the model, you can download the standalone executable archived in a zip file for your operating system.

- ⊞ **Windows:** [refer to the corresponding .zip file for windows in latest release](https://github.com/hamedonline/MiMoQuant/releases/latest)
- 🐧 **Linux:** [refer to the corresponding zip archive file for linux in latest release](https://github.com/hamedonline/MiMoQuant/releases/latest)
- 🍎 **macOS:** No releases yet, you need to build it from source.

**Setup:** Simply download the archive file, extract it, and run the executable. No Python installation is required.

---

## 🧑‍💻 Development and Running from Source

To play with the source code or run the software from source, you need to clone the repository and install the requirements.

```bash
git clone https://github.com/hamedonline/MiMoQuant.git
cd MiMoQuant/src
```

You need to create a virtual environment and install the required dependencies. The recommended Python version is 3.12 or higher. We recommend using a new separate virtual environment to avoid conflicts with other Python packages you may already have on your system. Any virtual environment handler or package manager of your choice can be used (e.g., `venv`, `conda`, `virtualenv`, etc.). However, we recommend [UV](https://github.com/astral-sh/uv).

First, make sure you are in the `MiMoQuant/src` folder and then run the following commands in your terminal to create a virtual environment and install the required dependencies:

```bash
uv venv --python 3.12
uv add -r requirements.txt
```

and then run the main program:

```bash
uv run python -m main
```

---

## 💻 Building from Source

MiMoQuant binaries can be built from source code using tools like `pyinstaller` ([PyInstaller Documentation](https://pyinstaller.org/)). To ease the process of compiling the software with PyInstaller, we provide a Spec file (`src/MiMoQuant.spec`) that contains the necessary configuration for building the executable. You can use this spec file to create a standalone executable for your desired operating system:

```bash
> cd MiMoQuant/src
> pyinstaller MiMoQuant.spec
```

Wait for the build process to complete. The resulting executable will be located in the `dist/` directory.

---

## ⚙️ Running the Main Program

Whether you use executables or compile from source, working with MiMoQuant is quite straightforward. Watch the introductory video to learn how to use the software effectively:

[MiMoQuant Introductory Video](https://www.youtube.com/watch?v=UVJ0hZ2DIGA).

Note: a shorter and more focused video is in preparation and will be available soon.

---

## 🗃️ Dataset and Sample Images

The dataset used for training and evaluating the MiMoQuant tool is available in a separate [repository in ZENODO](https://zenodo.org/records/23413787). It contains the collection of 2D microscopy images of mitochondrial morphology and corresponding annotations that were used to train the analysis model. Furthermore, the dataset contains annotation metadata compatible with MiMoQuant, alongside the algorithmically generated bounding-box JSON files for each image, compatible with [labelme](https://github.com/wkentaro/labelme).

Moreover, we provide sample images if you want to test the software without downloading the full dataset. These images are located in the `sample_images/` folder of this repository. Both Whole Slide Images (WSI) and cropped samples of Regions of Interest (ROIs) are provided as the sample data. The images used for the publication figures are also included in a separate file.

```text
sample_images/
├── Publication-Images.zip
└── Sample-Images.zip
```

---

## 🧠 Model Retraining

Refer to the [`/retraining`](retraining/README.md) folder for detailed instructions on how to retrain the analysis model using your own annotated images. This includes steps for data preparation, model training, and converting trained weights for inference in MiMoQuant.

---

## 📜 Citation

Stay tuned for the official citation information once the paper is published.

If you use this software, the dataset, or the underlying methodologies in your research, please consider coming back to this repository for the official citation format.

Meanwhile, the dataset can be cited using the following DOI link: [https://doi.org/10.5281/zenodo.23413787](https://doi.org/10.5281/zenodo.23413787).

---

## 🤝 License & Acknowledgements

- **License:**
  - This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
  - The dataset is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0) - see the LICENSE file in the dataset repository for details.
- **Acknowledgements:** [YOLOX](https://github.com/Megvii-BaseDetection/YOLOX) is utilized as the underlying object detection model in MiMoQuant. We thank the Megvii research team for their open-source contributions.
- **Funding:** This research was funded by Austrian Science Fund (FWF) under grant number [10.55776/FG15](https://www.fwf.ac.at/en/research-radar/10.55776/FG15). It was developed in collaboration of Universität Innsbruck and Medizinische Universität Innsbruck.
