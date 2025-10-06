"""
Configuration file for late_fusion system.
Adjust these settings to fine-tune detection sensitivity.
"""


# ADB Configuration

SDK_ADB = "/Users/rayidalshammari/Library/Android/sdk/platform-tools/adb"


# Clip Processing Settings

CLIP_SIZE = 15
FRAME_SKIP = 1

# Detection Thresholds


# Nudity Detection (NudeNet)
NUDITY_THRESHOLD = 0.6

# Wealth Detection (YOLO)
WEALTH_THRESHOLD = 0.5

# Child Detection - Per Frame
CHILD_CONF_THRESHOLD = 0.25            
CHILD_MINIMUM_DECISION_SCORE = 0.45     

# Child Detection - Per Class
CONF_THRESHOLD_CHILD = 0.25   
CONF_THRESHOLD_ADULT = 0.70  


# Child Detection - Scene Level


# Tracker Settings
IOU_TRACKER_TH = 0.40        # IoU threshold for tracking (lower = more lenient)
TRACKER_MAX_LOST = 8         # Max frames a track can be lost before deletion
CENTER_FRAC = 0.35           # Central area fraction (0.35 = ±35% from center)

# CONFIRMED Criteria (Very strict - high confidence exploitation)
CHILD_APPEAR_RATIO_CONFIRMED = 0.50     # Child appears in 50%+ of frames
CHILD_CENTERED_RATIO_CONFIRMED = 0.40   # Centered in 40%+ of appearances
CHILD_CONF_CONFIRMED = 0.60             # Average confidence 60%+
CHILD_MIN_SIZE_CONFIRMED = 0.03         # Minimum 3% of frame area

# SUSPECT Criteria (Less strict - needs review)
CHILD_APPEAR_RATIO_SUSPECT = 0.30       # Child appears in 30%+ of frames
CHILD_CENTERED_RATIO_SUSPECT = 0.30     # Centered in 30%+ of appearances
CHILD_CONF_SUSPECT_MIN = 0.35           # Minimum confidence 35%
CHILD_CONF_SUSPECT_MAX = 0.65           # Maximum confidence 65%
CHILD_MIN_SIZE_SUSPECT = 0.02           # Minimum 2% of frame area


# Output Settings

OUTPUT_DIR = "violations"   # Directory to save violation images and JSON


# Model Paths

CHILD_MODEL_PATH = "models/Child_Detection_Model.pt"
WEALTH_MODEL_PATH = "models/Currency_Detection_Model.pt"


# Tips for Tuning

"""
إذا لم يتم كشف الأطفال:
1. خفض CHILD_CONF_THRESHOLD إلى 0.15
2. خفض CHILD_MINIMUM_DECISION_SCORE إلى 0.30
3. خفض CHILD_APPEAR_RATIO_SUSPECT إلى 0.20
4. زد CLIP_SIZE إلى 20 أو 30

إذا كانت الكشوفات كثيرة جداً (false positives):
1. ارفع CHILD_CONF_THRESHOLD إلى 0.35
2. ارفع CHILD_MINIMUM_DECISION_SCORE إلى 0.55
3. ارفع CHILD_APPEAR_RATIO_SUSPECT إلى 0.40

لتحسين الأداء:
1. زد FRAME_SKIP إلى 2 أو 3
2. قلل CLIP_SIZE إلى 10
"""