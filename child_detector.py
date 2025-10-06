"""
Child detector (scene-level) using YOLO .pt + SimpleIouTracker.
Improved to distinguish between children (class 0) and adults (class 1).
Only tracks and reports children, ignores adults unless very high confidence of child.
"""

from ultralytics import YOLO
import torch
import numpy as np
from tracker_simple import SimpleIouTracker
import os

MODEL_PATH = "models/Child_Detection_Model.pt"

CHILD_CLASS_ID = 0
ADULT_CLASS_ID = 1

CONF_THRESHOLD_CHILD = 0.40
CONF_THRESHOLD_ADULT = 0.65


IOU_TRACKER_TH = 0.45
TRACKER_MAX_LOST = 6


CENTER_FRAC = 0.30


CHILD_APPEAR_RATIO_CONFIRMED = 0.6
CHILD_CENTERED_RATIO_CONFIRMED = 0.5
CHILD_CONF_CONFIRMED = 0.70
CHILD_MIN_SIZE_CONFIRMED = 0.05


CHILD_APPEAR_RATIO_SUSPECT = 0.4
CHILD_CENTERED_RATIO_SUSPECT = 0.4
CHILD_CONF_SUSPECT_MIN = 0.45
CHILD_CONF_SUSPECT_MAX = 0.70
CHILD_MIN_SIZE_SUSPECT = 0.03


device = "cuda" if torch.cuda.is_available() else "cpu"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Child model not found at {MODEL_PATH}")

model = YOLO(MODEL_PATH)
print(f"[child_detector] Loaded model on {device}")


tracker = SimpleIouTracker(iou_threshold=IOU_TRACKER_TH, max_lost_frames=TRACKER_MAX_LOST)


def is_centered(box, img_w, img_h, center_frac=CENTER_FRAC):
    """Check if box center is within central region of frame."""
    cx = (box[0] + box[2]) / 2.0
    cy = (box[1] + box[3]) / 2.0
    left = img_w * (0.5 - center_frac/2)
    right = img_w * (0.5 + center_frac/2)
    top = img_h * (0.5 - center_frac/2)
    bottom = img_h * (0.5 + center_frac/2)
    return (left <= cx <= right) and (top <= cy <= bottom)

def area(box):
    """Calculate box area."""
    w = max(0, box[2]-box[0])
    h = max(0, box[3]-box[1])
    return w*h

def detect_children_on_frame(frame, conf=0.35, imgsz=640):
    """
    Run YOLO model on frame and return ONLY child detections (class 0).
    Adults (class 1) are filtered out unless confidence is extremely high.
    
    Returns: list of {'bbox':[x1,y1,x2,y2], 'score':float, 'class_id':int}
    """
    try:
        results = model.predict(source=frame, imgsz=imgsz, conf=conf, device=device, verbose=False)
    except Exception:
        return []

    dets = []
    for r in results:
        if not hasattr(r, "boxes") or r.boxes is None:
            continue
        
        for b in r.boxes:
            conf_score = float(b.conf[0].item())
            cls_id = int(b.cls[0].item())
            xyxy = b.xyxy[0].tolist()
            

            if cls_id == CHILD_CLASS_ID:

                if conf_score >= CONF_THRESHOLD_CHILD:
                    dets.append({
                        "bbox": [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])],
                        "score": conf_score,
                        "class_id": cls_id
                    })
            elif cls_id == ADULT_CLASS_ID:

                if conf_score >= CONF_THRESHOLD_ADULT:


                    pass
    
    return dets

def analyze_clip_for_child(frames, conf=0.35, imgsz=640):
    """
    Analyze a clip of frames for child exploitation indicators.
    
    Args:
        frames: list of BGR numpy frames (clip)
        conf: confidence threshold (will use class-specific thresholds internally)
        imgsz: inference image size
    
    Returns:
        dict with structure:
        {
            "final_decision": "CONFIRMED" | "SUSPECT" | "NONE",
            "score": float (0-1),
            "top_id": int or None (track ID),
            "top_bbox": [x1,y1,x2,y2] or None,
            "metrics_by_id": {track_id: {...metrics...}},
            "severity_by_id": {track_id: {...severity...}},
            "top_frame": numpy_image or None
        }
    """
    if not frames:
        return {
            "final_decision": "NONE",
            "score": 0.0,
            "top_id": None,
            "top_bbox": None,
            "metrics_by_id": {},
            "severity_by_id": {},
            "top_frame": None
        }


    local_tracker = SimpleIouTracker(iou_threshold=IOU_TRACKER_TH, max_lost_frames=TRACKER_MAX_LOST)

    per_frame_detections = []
    assignments_history = []
    
    top_score_global = 0.0
    top_frame_global = None
    top_bbox_global = None
    top_id_global = None


    for frame_idx, frame in enumerate(frames):
        dets = detect_children_on_frame(frame, conf=conf, imgsz=imgsz)
        per_frame_detections.append(dets)
        

        assignment = local_tracker.update(dets, frame_idx)
        assignments_history.append(assignment)
        

        for di, det in enumerate(dets):
            if det["score"] > top_score_global:
                top_score_global = det["score"]
                top_frame_global = frame.copy()
                top_bbox_global = det["bbox"]
                tid = assignment.get(di)
                top_id_global = tid

    total_frames = len(frames)
    tracks = local_tracker.get_tracks()


    id_presence_counts = {}
    id_center_counts = {}
    id_conf_sums = {}
    id_area_sums = {}
    id_occurrences = {}

    for fi, dets in enumerate(per_frame_detections):
        if not dets:
            continue
            
        h, w = frames[fi].shape[:2]
        assign = assignments_history[fi] if fi < len(assignments_history) else {}
        
        for di, det in enumerate(dets):
            tid = assign.get(di)
            if tid is None:
                continue
            

            id_presence_counts[tid] = id_presence_counts.get(tid, 0) + 1
            

            if is_centered(det["bbox"], w, h, center_frac=CENTER_FRAC):
                id_center_counts[tid] = id_center_counts.get(tid, 0) + 1
            

            id_conf_sums[tid] = id_conf_sums.get(tid, 0.0) + det["score"]
            id_area_sums[tid] = id_area_sums.get(tid, 0.0) + (area(det["bbox"]) / (w * h))
            id_occurrences[tid] = id_occurrences.get(tid, 0) + 1


    metrics_by_id = {}
    for tid, info in tracks.items():
        pres = id_presence_counts.get(tid, 0)
        occ = id_occurrences.get(tid, 0)
        centered = id_center_counts.get(tid, 0)
        
        avg_conf = (id_conf_sums.get(tid, 0.0) / occ) if occ > 0 else 0.0
        avg_size_ratio = (id_area_sums.get(tid, 0.0) / occ) if occ > 0 else 0.0
        appearance_ratio = pres / total_frames if total_frames > 0 else 0.0
        centered_ratio = centered / pres if pres > 0 else 0.0
        
        metrics_by_id[tid] = {
            "appearance_ratio": appearance_ratio,
            "centered_ratio": centered_ratio,
            "avg_confidence": avg_conf,
            "avg_size_ratio": avg_size_ratio,
            "last_bbox": info.get("last_bbox"),
            "lifespan": info.get("lifespan"),
            "presence_count": pres,
            "centered_count": centered
        }


    severity_by_id = {}
    for tid, m in metrics_by_id.items():
        severity = "NONE"
        score_summary = m["avg_confidence"]
        

        if (m["appearance_ratio"] >= CHILD_APPEAR_RATIO_CONFIRMED
            and m["centered_ratio"] >= CHILD_CENTERED_RATIO_CONFIRMED
            and m["avg_confidence"] >= CHILD_CONF_CONFIRMED
            and m["avg_size_ratio"] >= CHILD_MIN_SIZE_CONFIRMED):
            severity = "CONFIRMED"
        

        elif (m["appearance_ratio"] >= CHILD_APPEAR_RATIO_SUSPECT
              and m["centered_ratio"] >= CHILD_CENTERED_RATIO_SUSPECT
              and CHILD_CONF_SUSPECT_MIN <= m["avg_confidence"] < CHILD_CONF_SUSPECT_MAX
              and m["avg_size_ratio"] >= CHILD_MIN_SIZE_SUSPECT):
            severity = "SUSPECT"
        
        severity_by_id[tid] = {"severity": severity, "score": score_summary}


    final_decision = "NONE"
    final_score = 0.0
    final_id = None
    final_bbox = None
    final_frame = None


    for tid, s in severity_by_id.items():
        if s["severity"] == "CONFIRMED" and s["score"] > final_score:
            final_decision = "CONFIRMED"
            final_score = s["score"]
            final_id = tid
            final_bbox = metrics_by_id[tid]["last_bbox"]


    if final_decision == "NONE":
        for tid, s in severity_by_id.items():
            if s["severity"] == "SUSPECT" and s["score"] > final_score:
                final_decision = "SUSPECT"
                final_score = s["score"]
                final_id = tid
                final_bbox = metrics_by_id[tid]["last_bbox"]


    if final_decision == "NONE" and top_score_global >= CHILD_CONF_SUSPECT_MIN:
        final_decision = "SUSPECT"
        final_score = top_score_global
        final_id = top_id_global
        final_bbox = top_bbox_global
        final_frame = top_frame_global


    if final_id is not None:

        for fi, assignment in enumerate(assignments_history):
            if any(tid == final_id for tid in assignment.values()):
                final_frame = frames[fi].copy()
                break
        if final_frame is None:
            final_frame = top_frame_global
    else:
        final_frame = top_frame_global

    return {
        "final_decision": final_decision,
        "score": float(final_score),
        "top_id": int(final_id) if final_id is not None else None,
        "top_bbox": list(final_bbox) if final_bbox is not None else None,
        "metrics_by_id": metrics_by_id,
        "severity_by_id": severity_by_id,
        "top_frame": final_frame
    }