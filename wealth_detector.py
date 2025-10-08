from ultralytics import YOLO
import torch


MODEL_PATH = "models/Currency_Detection_Model.pt"
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    model = YOLO(MODEL_PATH)  
    print(f"[wealth_detector] Loaded model: {MODEL_PATH} on {device}")
except Exception as e:
    raise RuntimeError(f"[wealth_detector] Failed to load model '{MODEL_PATH}': {e}")

WEALTH_LABEL_KEYWORDS = ["wallet","money","cash","phone","watch","jewelry","car","handbag","laptop","wallet","credit"]

def detect_wealth(frame, conf_threshold=0.4, imgsz=640):
    """
    returns list of detections: {category, score, bbox:[x1,y1,x2,y2]}
    Uses ultralytics YOLO.predict on frame (numpy)
    """
    try:
        results = model.predict(source=frame, imgsz=imgsz, conf=conf_threshold, device=device, verbose=False)
    except Exception as e:
        
        return []

    out = []
    for r in results:

        if hasattr(r, "boxes") and r.boxes is not None:
            for b in r.boxes:
                conf = float(b.conf[0].item())
                cls = int(b.cls[0].item())
                xyxy = b.xyxy[0].tolist()  
                label = model.model.names.get(cls, str(cls)).lower()

                match = any(kw in label for kw in WEALTH_LABEL_KEYWORDS)
                if match or conf >= conf_threshold:
                    out.append({
                        "category": label,
                        "score": conf,
                        "bbox": [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])]
                    })
    return out
