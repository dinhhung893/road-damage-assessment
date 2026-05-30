# 🛣️ Road Damage Assessment System

An AI-powered desktop application for detecting and assessing pavement damage from images and video, using deep learning (YOLOv12s) and ASTM D6433 standard PCI calculation.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![PySide6](https://img.shields.io/badge/GUI-PySide6-green) ![YOLOv12](https://img.shields.io/badge/Detection-YOLOv12s-orange)

## Features

- **🔍 Damage Detection** — YOLOv12s model detects 4 damage types: longitudinal cracks (D00), transverse cracks (D10), alligator cracks (D20), and potholes (D40)
- **📐 PCI Calculation** — Pavement Condition Index following ASTM D6433 standard, with deduct value curves and severity assignment
- **✂️ FastSAM Segmentation** — Instance segmentation for precise damage boundary detection
- **🖥️ Desktop GUI** — PySide6 Fluent Design interface with Vietnamese UI
- **🎬 Video Processing** — Frame-by-frame analysis with OpenCV + FFmpeg H.264 encoding
- **📊 Export** — CSV/Excel reports with damage inventory and PCI ratings

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Image /    │────▶│   YOLOv12s   │────▶│  FastSAM    │
│   Video      │     │  Detection   │     │ Segmentation│
└─────────────┘     └──────┬───────┘     └──────┬──────┘
                           │                     │
                    Bounding Boxes          Instance Masks
                           │                     │
                           ▼                     ▼
                    ┌──────────────────────────────┐
                    │       PCI Engine             │
                    │   (ASTM D6433 Standard)      │
                    │  Deduct Values → CDV → PCI   │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │    PySide6 Desktop GUI        │
                    │  Image Viewer | PCI Gauge     │
                    │  Damage Table | Log Panel     │
                    └──────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Object Detection | YOLOv12s (Ultralytics) |
| Segmentation | FastSAM (ONNX Runtime) |
| PCI Engine | ASTM D6433 deduct value curves |
| GUI | PySide6 + Fluent Widgets |
| Video | OpenCV + FFmpeg |
| Inference | PyTorch CPU / ONNX Runtime DirectML |
| Language | Python 3.12 |

## Project Structure

```
src/
├── engine/
│   ├── detector.py      # YOLOv12s road damage detection
│   ├── pci.py           # PCI calculation (ASTM D6433)
│   └── segmenter.py     # FastSAM instance segmentation
├── ui/
│   ├── main_window.py   # Main application window
│   ├── settings_dialog.py
│   ├── strings.py       # Vietnamese/English UI strings
│   ├── workers.py       # QThread background workers
│   └── widgets/
│       ├── damage_table.py
│       ├── image_viewer.py
│       ├── log_panel.py
│       └── pci_gauge.py
└── utils/
    ├── config.py        # JSON-based config persistence
    ├── io.py            # File I/O helpers
    └── logging_setup.py # Rotating file handler
```

## Getting Started

### Prerequisites

- Python 3.12+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/road-damage-assessment.git
cd road-damage-assessment

# Create virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download model weights
python scripts/download_model.py
```

### Usage

```bash
# Launch the desktop application
python -m src
```

### Running Tests

```bash
pytest tests/
```

## Damage Classes

| Code | Type | Description |
|------|------|-------------|
| D00 | Longitudinal Crack | Crack running parallel to road direction |
| D10 | Transverse Crack | Crack running across road direction |
| D20 | Alligator Crack | Interconnected crack pattern (fatigue) |
| D40 | Pothole | Bowl-shaped depression in pavement |

## PCI Rating Scale (ASTM D6433)

| PCI Range | Rating | Condition |
|-----------|--------|-----------|
| 85-100 | Good | No significant deterioration |
| 70-85 | Satisfactory | Minor deterioration |
| 55-70 | Fair | Moderate deterioration |
| 40-55 | Poor | Significant deterioration |
| 25-40 | Very Poor | Extensive deterioration |
| 0-25 | Serious | Needs immediate attention |

## Model Performance

- **Model:** YOLOv12s (pretrained on RDD2022 benchmark)
- **mAP50:** 0.632
- **Inference:** ~896ms mean on Intel i5-4300U CPU
- **Source:** [SreekarAditya/yolo-rdd2022-benchmark](https://huggingface.co/SreekarAditya/yolo-rdd2022-benchmark)

## License

This project is developed for academic research purposes.

## Acknowledgments

- YOLOv12s model from [HuggingFace RDD2022 Benchmark](https://huggingface.co/SreekarAditya/yolo-rdd2022-benchmark)
- PCI calculation based on ASTM D6433 standard
- Built with [Ultralytics](https://ultralytics.com/) and [PySide6](https://doc.qt.io/qtforpython-6/)
