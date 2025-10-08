from nudenet import NudeDetector

detector = NudeDetector()  

def detect_nudity(frame, conf_threshold=0.6):
    """
    frame: BGR numpy image
    returns: list of dicts { "category": str, "score": float, "bbox": [x1,y1,x2,y2] or None }
    Note: NudeNet returns 'class' or 'label' and may supply 'box' or 'bbox' (either normalized or absolute).
    We pass bbox through (late fusion will interpret).
    We IGNORE any classes that contain 'face'.
    """
    out = []
    try:
        results = detector.detect(frame)
    except Exception:
        results = []

    for item in results:
        cat = item.get("class") or item.get("label") or None
        if not cat:
            continue
        if "face" in cat.lower():
            continue
        score = float(item.get("score", 0) or 0)
        if score < conf_threshold:
            continue
        bbox = item.get("box") or item.get("bbox") or None
        out.append({"category": cat, "score": score, "bbox": bbox})
    return out



