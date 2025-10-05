#          لتشغيل هذا الملف، تأكد من تثبيت المكتبات المطلوبة:
#         pip install opencv-python nudenet numpy
#         !/usr/bin/env python3
#         detect_nudity_realtime.py

import os
import time
import subprocess
from datetime import datetime
import numpy as np
import cv2
from nudenet import NudeDetector

# Configuration
SDK_ADB = "/Users/rayidalshammari/Library/Android/sdk/platform-tools/adb"
OUTPUT_DIR = "alerts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BATCH_SIZE = 5          # عدد الفريمات في المشهد (clip)
FPS = 1                 # تكرار أخذ الفريمات (fps) من المحاكي
THRESHOLD = 0.6         # الثقة للموافقة على وجود مخالفة في المشهد

# تجاهل الوجوه
IGNORED_LABELS = {"FACE_FEMALE", "FACE_MALE"}

CATEGORY_AR = {
    "FEMALE_BREAST_EXPOSED": "صدر أنثوي مكشوف",
    "FEMALE_GENITALIA_EXPOSED": "أعضاء تناسلية أنثوية مكشوفة",
    "MALE_GENITALIA_EXPOSED": "أعضاء تناسلية ذكرية مكشوفة",
    "BUTTOCKS_EXPOSED": "أرداف مكشوفة",
    "ANUS_EXPOSED": "الشرج مكشوف",
    "BELLY_EXPOSED": "بطن مكشوف",
    "SHOULDERS_TO_KNEES_EXPOSED": "الكشف من الكتفين إلى الركبتين"
}

# Initialize detector
detector = NudeDetector()



# التقاط الفريم من المحاكي
def capture_frame_from_emulator():
    try:
        cmd = [SDK_ADB, "exec-out", "screencap", "-p"]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=8)
        if p.returncode != 0 or not p.stdout:
            return None
        img_bytes = np.frombuffer(p.stdout, dtype=np.uint8)
        frame = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"⚠️ capture error: {e}")
        return None

# تحليل مشهد من الفريمات
def analyze_clip(frames):
    per_category_scores = {}
    top_conf = 0.0
    top_frame = None
    top_info = None

    raw = []
    for frame in frames:
        if frame is None: 
            continue
        try:
            results = detector.detect(frame)
        except:
            results = []
        for item in results:
            cat = item.get("class") or item.get("label")
            score = float(item.get("score",0))

            if not cat or cat in IGNORED_LABELS:
                continue

            per_category_scores.setdefault(cat,[]).append(score)

            if score > top_conf:
                top_conf = score
                top_frame = frame.copy()
                top_info = {"category":cat,"score":score}

        raw.append(results)

    avg_scores = {c:float(np.mean(s)) for c,s in per_category_scores.items() if s}
    return avg_scores, top_frame, top_info





# Main loop 
def main_loop():
    print(" بدء المراقبة من المحاكي (Ctrl+C للإيقاف)...")
    batch = []
    try:
        while True:
            frame = capture_frame_from_emulator()
            if frame is not None:
                batch.append(frame)

            if len(batch) >= BATCH_SIZE:
                avg_scores, top_frame, top_info = analyze_clip(batch)
                alerted = {c:s for c,s in avg_scores.items() if s>=THRESHOLD}

                if alerted and top_frame is not None and top_info:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    path = os.path.join(OUTPUT_DIR, f"alert_{ts}.jpg")
                    cv2.imwrite(path, top_frame)

                    cat = top_info["category"]
                    conf = top_info["score"]
                    print(f" مخالفة: {CATEGORY_AR.get(cat,cat)} | الثقة: {conf:.2f}")
                    print(f" تم حفظ الصورة: {path}")
                else:
                    print(".", end="", flush=True)

                batch=[]
            time.sleep(1.0/FPS)
    except KeyboardInterrupt:
        print("\n تم إيقاف المراقبة.")

if __name__ == "__main__":
    main_loop()
