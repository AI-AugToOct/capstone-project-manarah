# tracker_simple.py
"""
Simple IoU-based tracker.
Keeps short history per track and assigns incremental IDs.
No external deps.
"""

import time

class Track:
    def __init__(self, tid, bbox, score, frame_idx):
        self.id = tid
        self.bboxes = [bbox]        # history of bbox [x1,y1,x2,y2]
        self.scores = [score]
        self.last_seen = frame_idx
        self.first_seen = frame_idx
        self.active = True

    def update(self, bbox, score, frame_idx):
        self.bboxes.append(bbox)
        self.scores.append(score)
        self.last_seen = frame_idx

    def last_bbox(self):
        return self.bboxes[-1]

    def avg_score(self):
        return sum(self.scores) / len(self.scores)

    def lifespan(self):
        return self.last_seen - self.first_seen + 1

class SimpleIouTracker:
    def __init__(self, iou_threshold=0.4, max_lost_frames=5):
        self.iou_threshold = iou_threshold
        self.max_lost_frames = max_lost_frames
        self.tracks = {}  # tid -> Track
        self._next_id = 1

    @staticmethod
    def iou(boxA, boxB):
        # boxes: [x1,y1,x2,y2]
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interW = max(0, xB - xA)
        interH = max(0, yB - yA)
        interArea = interW * interH
        boxAArea = max(0, boxA[2]-boxA[0]) * max(0, boxA[3]-boxA[1])
        boxBArea = max(0, boxB[2]-boxB[0]) * max(0, boxB[3]-boxB[1])
        denom = float(boxAArea + boxBArea - interArea)
        return interArea / denom if denom > 0 else 0.0

    def update(self, detections, frame_idx):
        """
        detections: list of dicts: {'bbox':[x1,y1,x2,y2], 'score':float}
        frame_idx: current frame index (int)
        returns mapping det_idx -> track_id
        """
        assignments = {}
        unmatched_dets = set(range(len(detections)))
        # compute IoU matrix between last bboxes of tracks and new detections
        track_ids = list(self.tracks.keys())
        if track_ids and detections:
            iou_mat = []
            for tid in track_ids:
                tb = self.tracks[tid].last_bbox()
                row = [self.iou(tb, det['bbox']) for det in detections]
                iou_mat.append(row)
            # greedy matching: pick highest IoU pairs
            used_tracks = set()
            used_dets = set()
            # flatten with indices
            flat = []
            for i, tid in enumerate(track_ids):
                for j in range(len(detections)):
                    flat.append((iou_mat[i][j], i, j))
            flat.sort(reverse=True, key=lambda x: x[0])
            for val, i, j in flat:
                if val < self.iou_threshold:
                    break
                if i in used_tracks or j in used_dets:
                    continue
                tid = track_ids[i]
                self.tracks[tid].update(detections[j]['bbox'], detections[j]['score'], frame_idx)
                assignments[j] = tid
                used_tracks.add(i)
                used_dets.add(j)
                unmatched_dets.discard(j)
        # create new tracks for unmatched detections
        for det_idx in list(unmatched_dets):
            det = detections[det_idx]
            tid = self._next_id
            self._next_id += 1
            self.tracks[tid] = Track(tid, det['bbox'], det['score'], frame_idx)
            assignments[det_idx] = tid
        # cleanup lost tracks
        to_delete = []
        for tid, tr in self.tracks.items():
            if frame_idx - tr.last_seen > self.max_lost_frames:
                to_delete.append(tid)
        for tid in to_delete:
            del self.tracks[tid]
        return assignments

    def get_tracks(self):
        """Return shallow summary of active tracks"""
        out = {}
        for tid, tr in self.tracks.items():
            out[tid] = {
                "id": tid,
                "last_seen": tr.last_seen,
                "first_seen": tr.first_seen,
                "lifespan": tr.lifespan(),
                "last_bbox": tr.last_bbox(),
                "avg_score": tr.avg_score(),
                "history_len": len(tr.bboxes)
            }
        return out
