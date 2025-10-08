#  Real-Time Violation Detection Branch

This branch focuses exclusively on **real-time detection and fusion logic** for visual violations, independent from the main project pipeline.  
It serves as a **modular research branch** to test detection accuracy, model behavior, and performance under live conditions.

---

##  Purpose

The goal of this branch is to **integrate and test multiple vision models** that detect visual policy violations in real-time directly from an Android emulator using `adb`.  
It provides a unified framework to combine detections of:

1. **Child Exploitation Content** — using `Child_Detection_Model.pt / .onnx`  
2. **Wealth & Money Bragging** — using `Currency_Detection_Model.pt / .onnx`  
3. **Nudity or Restricted Body Exposure** — using `NudeNet` or similar detector  

All results are **merged and filtered** using the logic in `late_fusion.py`, producing a single JSON + image output per violation.

---

##  Branch Structure

branch/
├── child_detector.py # Child content detection module
├── detect_nudity_realtime.py # Nudity detection (real-time)
├── wealth_detector.py # Wealth/money bragging detection
├── late_fusion.py # Fusion and logic layer (core)
├── tracker_simple.py # Object tracking (optional)
├── utils.py # Helper functions
├── config.py # Configuration paths and ADB setup
├── requirements.txt # Dependencies for this branch
├── notebooks/ # Training and testing notebooks
│ ├── Child_Detection_Model.ipynb
│ └── Currency_Detection_Model.ipynb
├── models/ # Pre-trained models (.pt / .onnx)
├── violations/ # Output violations (images + JSON)
│ ├── child_.json/.jpg
│ ├── wealth_.json/.jpg
│ └── nudity_*.json/.jpg


---

##  Running This Branch

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure the ADB path
Edit config.py and set:
```bash
SDK_ADB = "Android/sdk/platform-tools/adb"
```
### 3. Run real-time fusion logic
```bash
python late_fusion.py
```
This will:

Continuously capture emulator frames.

Run detection models (child, wealth, nudity).

Merge results and export JSON/image outputs for each violation.

### Notes

If multiple violations are found in one frame, they’re all logged in the same JSON entry.

Detection thresholds and model confidence can be tuned inside config.py.

Designed to test live moderation pipelines before integration into the main project.

