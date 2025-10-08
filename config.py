"""
Configuration file for late_fusion system.
Adjust these settings to fine-tune detection sensitivity.
"""



SDK_ADB = "/Users/rayidalshammari/Library/Android/sdk/platform-tools/adb"



CLIP_SIZE = 15
FRAME_SKIP = 1



NUDITY_THRESHOLD = 0.6

WEALTH_THRESHOLD = 0.5

CHILD_CONF_THRESHOLD = 0.25            
CHILD_MINIMUM_DECISION_SCORE = 0.45     

CONF_THRESHOLD_CHILD = 0.25   
CONF_THRESHOLD_ADULT = 0.70  




IOU_TRACKER_TH = 0.40        
TRACKER_MAX_LOST = 8
CENTER_FRAC = 0.35          

CHILD_APPEAR_RATIO_CONFIRMED = 0.50     
CHILD_CENTERED_RATIO_CONFIRMED = 0.40   
CHILD_CONF_CONFIRMED = 0.60             
CHILD_MIN_SIZE_CONFIRMED = 0.03         


CHILD_APPEAR_RATIO_SUSPECT = 0.30       
CHILD_CENTERED_RATIO_SUSPECT = 0.30    
CHILD_CONF_SUSPECT_MIN = 0.35           
CHILD_CONF_SUSPECT_MAX = 0.65           
CHILD_MIN_SIZE_SUSPECT = 0.02           




OUTPUT_DIR = "violations"   




CHILD_MODEL_PATH = "models/Child_Detection_Model.pt"
WEALTH_MODEL_PATH = "models/Currency_Detection_Model.pt"




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