"""
Multi-detector system for Android emulator monitoring:
- Processes video in clips (batches of frames)
- Detects: nudity, child exploitation, wealth display
- Saves violations as separate image + JSON per type
- Smart terminal output (dots for clean, alerts for violations)
- Arabic output for violation types
"""

import cv2
import subprocess
import numpy as np
import os
import json
import time
import sys
from datetime import datetime
from collections import deque


from detect_nudity_realtime import detect_nudity
from child_detector import analyze_clip_for_child
from wealth_detector import detect_wealth





SDK_ADB = "/Users/rayidalshammari/Library/Android/sdk/platform-tools/adb"


CLIP_SIZE = 15  
FRAME_SKIP = 1  


NUDITY_THRESHOLD = 0.6
WEALTH_THRESHOLD = 0.5
CHILD_CONF_THRESHOLD = 0.25  
CHILD_MINIMUM_DECISION_SCORE = 0.45  

OUTPUT_DIR = "violations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.path.exists(SDK_ADB):
    raise FileNotFoundError(f"ADB not found at {SDK_ADB}")

print(f"[system] تم التهيئة - حجم الكليب: {CLIP_SIZE}, تخطي الإطارات: {FRAME_SKIP}")


def get_emulator_frame():
    """Capture single frame from Android emulator via ADB screencap."""
    try:
        process = subprocess.Popen(
            [SDK_ADB, "exec-out", "screencap", "-p"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        frame_bytes = process.stdout.read()
        process.wait()
        
        if not frame_bytes:
            return None
            
        img_array = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"\n[خطأ] فشل التقاط الإطار: {e}")
        return None


def detect_violations_in_clip(frames):
    """
    Analyze a clip for all violation types.
    Returns: dict with keys: 'child', 'nudity', 'wealth'
    Each value is None or detection data.
    """
    violations = {
        'child': None,
        'nudity': None,
        'wealth': None
    }
    
    print(f"[تحليل] فحص استغلال الأطفال في {len(frames)} إطار...", end=" ")
    child_result = analyze_clip_for_child(frames, conf=CHILD_CONF_THRESHOLD)
    
    print(f"النتيجة: {child_result['final_decision']}, النقاط: {child_result['score']:.2f}")
    
    if child_result['final_decision'] in ['CONFIRMED', 'SUSPECT']:
        if child_result['score'] >= CHILD_MINIMUM_DECISION_SCORE:
            violations['child'] = child_result
            print(f"   ✓ تم رصد استغلال أطفال ({child_result['final_decision']})")
    
    nudity_detections = []
    best_nudity_frame = None
    best_nudity_score = 0.0
    
    for frame in frames:
        dets = detect_nudity(frame, conf_threshold=NUDITY_THRESHOLD)
        if dets:
            for det in dets:
                if det['score'] > best_nudity_score:
                    best_nudity_score = det['score']
                    best_nudity_frame = frame
                nudity_detections.append(det)
    
    if nudity_detections:
        violations['nudity'] = {
            'detections': nudity_detections,
            'max_score': best_nudity_score,
            'frame': best_nudity_frame if best_nudity_frame is not None else frames[-1]
        }
    
    wealth_detections = []
    best_wealth_frame = None
    best_wealth_score = 0.0
    
    for frame in frames:
        dets = detect_wealth(frame, conf_threshold=WEALTH_THRESHOLD)
        if dets:
            for det in dets:
                if det['score'] > best_wealth_score:
                    best_wealth_score = det['score']
                    best_wealth_frame = frame
                wealth_detections.append(det)
    
    if wealth_detections:
        violations['wealth'] = {
            'detections': wealth_detections,
            'max_score': best_wealth_score,
            'frame': best_wealth_frame if best_wealth_frame is not None else frames[-1]
        }
    
    return violations

def save_child_violation(child_data, timestamp):
    """Save child violation with single bounding box for most confident detection."""
    frame = child_data.get('top_frame')
    if frame is None:
        return None
    
    img_path = os.path.join(OUTPUT_DIR, f"child_{timestamp}.jpg")
    json_path = os.path.join(OUTPUT_DIR, f"child_{timestamp}.json")
    
    frame_copy = frame.copy()
    bbox = child_data.get('top_bbox')
    
    if bbox:
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 0, 255), 3)
        
        decision_ar = "مؤكد" if child_data['final_decision'] == 'CONFIRMED' else "مشتبه"
        label = f"Child {decision_ar} {child_data['score']:.2f}"
        cv2.putText(frame_copy, label, (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    cv2.imwrite(img_path, frame_copy)
    
    json_data = {
        'type': 'child_exploitation',
        'type_ar': 'استغلال أطفال',
        'timestamp': timestamp,
        'decision': child_data['final_decision'],
        'score': child_data['score'],
        'track_id': child_data.get('top_id'),
        'bbox': bbox,
        'metrics': child_data.get('metrics_by_id', {}),
        'severity_by_id': child_data.get('severity_by_id', {})
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return img_path

def save_nudity_violation(nudity_data, timestamp):
    """Save nudity violation (no bounding boxes, just scene image + JSON)."""
    frame = nudity_data['frame']
    
    img_path = os.path.join(OUTPUT_DIR, f"nudity_{timestamp}.jpg")
    json_path = os.path.join(OUTPUT_DIR, f"nudity_{timestamp}.json")
    
    cv2.imwrite(img_path, frame)
    
    json_data = {
        'type': 'nudity',
        'type_ar': 'محتوى إباحي',
        'timestamp': timestamp,
        'max_score': nudity_data['max_score'],
        'detections': [
            {
                'category': det['category'],
                'score': det['score'],
                'bbox': det.get('bbox')
            }
            for det in nudity_data['detections']
        ]
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return img_path

def save_wealth_violation(wealth_data, timestamp):
    """Save wealth violation (no bounding boxes, just scene image + JSON)."""
    frame = wealth_data['frame']
    
    img_path = os.path.join(OUTPUT_DIR, f"wealth_{timestamp}.jpg")
    json_path = os.path.join(OUTPUT_DIR, f"wealth_{timestamp}.json")
    
    cv2.imwrite(img_path, frame)
    
    json_data = {
        'type': 'wealth',
        'type_ar': 'عرض ثروة',
        'timestamp': timestamp,
        'max_score': wealth_data['max_score'],
        'detections': [
            {
                'category': det['category'],
                'score': det['score'],
                'bbox': det.get('bbox')
            }
            for det in wealth_data['detections']
        ]
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return img_path

def save_violations(violations):
    """Save all detected violations as separate files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    saved_files = []
    
    if violations['child']:
        path = save_child_violation(violations['child'], timestamp)
        if path:
            saved_files.append(('استغلال أطفال', path))
    
    if violations['nudity']:
        path = save_nudity_violation(violations['nudity'], timestamp)
        if path:
            saved_files.append(('محتوى إباحي', path))
    
    if violations['wealth']:
        path = save_wealth_violation(violations['wealth'], timestamp)
        if path:
            saved_files.append(('عرض ثروة', path))
    
    return saved_files


def main_loop():
    """Main monitoring loop with clip-based processing."""
    print(f"[نظام] بدء مراقبة السيميوليتر (Ctrl+C للإيقاف)...")
    print(f"[نظام] مجلد الحفظ: {OUTPUT_DIR}")
    print(f"[نظام] الرموز: . = نظيف، 🚨 = مخالفة\n")
    
    frame_buffer = deque(maxlen=CLIP_SIZE)
    frame_count = 0
    clip_count = 0
    
    try:
        while True:
           
            frame = get_emulator_frame()
            if frame is None:
                time.sleep(0.5)
                continue
            
            frame_count += 1
            
            
            if frame_count % FRAME_SKIP != 0:
                continue
            
            
            frame_buffer.append(frame)
            
            
            if len(frame_buffer) == CLIP_SIZE:
                clip_count += 1
                frames_list = list(frame_buffer)
                
                print(f"\n[كليب #{clip_count}] تحليل {len(frames_list)} إطار...")
                
                
                violations = detect_violations_in_clip(frames_list)
                
                
                has_violation = any(v is not None for v in violations.values())
                
                if has_violation:
                    
                    saved = save_violations(violations)
                    
                    
                    alerts = []
                    if violations['child']:
                        decision = violations['child']['final_decision']
                        decision_ar = "مؤكد" if decision == 'CONFIRMED' else "مشتبه"
                        score = violations['child']['score']
                        alerts.append(f"استغلال أطفال ({decision_ar}, {score:.2f})")
                    if violations['nudity']:
                        score = violations['nudity']['max_score']
                        alerts.append(f"محتوى إباحي ({score:.2f})")
                    if violations['wealth']:
                        score = violations['wealth']['max_score']
                        alerts.append(f"عرض ثروة ({score:.2f})")
                    
                    print(f"\n🚨 كليب #{clip_count}: {' + '.join(alerts)}")
                    for vtype, path in saved:
                        print(f"   └─ {vtype}: {path}")
                    
                    sys.stdout.flush()
                else:
                    
                    print(".", end="", flush=True)
                
                
                frame_buffer.clear()
            
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print(f"\n\n[نظام] تم الإيقاف. تم معالجة {clip_count} كليب ({frame_count} إطار).")
        print(f"[نظام] المخالفات محفوظة في: {OUTPUT_DIR}")



if __name__ == "__main__":
    main_loop()