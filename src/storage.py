"""Data storage module for JSON-based persistence."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from src.config import settings

logger = logging.getLogger(__name__)


def save_metadata(content_id: str, user_id: str, data: Dict[str, Any]) -> Path:
    """Save content metadata to JSON file.
    
    Args:
        content_id: Unique content identifier
        user_id: User identifier
        data: Metadata dictionary
        
    Returns:
        Path to saved metadata file
    """
    content_path = settings.content_dir / user_id / content_id
    content_path.mkdir(parents=True, exist_ok=True)
    
    metadata_path = content_path / "metadata.json"
    
    # Add timestamps
    if "upload_timestamp" not in data:
        data["upload_timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved metadata for content_id={content_id}")
    return metadata_path


def load_metadata(content_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Load content metadata from JSON file.
    
    Args:
        content_id: Unique content identifier
        user_id: User identifier
        
    Returns:
        Metadata dictionary or None if not found
    """
    metadata_path = settings.content_dir / user_id / content_id / "metadata.json"
    
    if not metadata_path.exists():
        logger.warning(f"Metadata not found for content_id={content_id}")
        return None
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_metadata(content_id: str, user_id: str, updates: Dict[str, Any]) -> None:
    """Update existing metadata with new fields.
    
    Args:
        content_id: Unique content identifier
        user_id: User identifier
        updates: Dictionary of fields to update
    """
    metadata = load_metadata(content_id, user_id)
    if metadata:
        metadata.update(updates)
        save_metadata(content_id, user_id, metadata)


def save_analysis(content_id: str, analysis: Dict[str, Any]) -> Path:
    """Save analysis results to JSON file.
    
    Args:
        content_id: Unique content identifier
        analysis: Analysis results dictionary
        
    Returns:
        Path to saved analysis file
    """
    analysis_path = settings.analysis_dir / f"{content_id}.json"
    
    # Add timestamp
    if "analysis_timestamp" not in analysis:
        analysis["analysis_timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    analysis["content_id"] = content_id
    
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved analysis for content_id={content_id}")
    return analysis_path


def load_analysis(content_id: str) -> Optional[Dict[str, Any]]:
    """Load analysis results from JSON file.
    
    Args:
        content_id: Unique content identifier
        
    Returns:
        Analysis dictionary or None if not found
    """
    analysis_path = settings.analysis_dir / f"{content_id}.json"
    
    if not analysis_path.exists():
        logger.warning(f"Analysis not found for content_id={content_id}")
        return None
    
    with open(analysis_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_decision(content_id: str, decision: Dict[str, Any]) -> Path:
    """Save decision results to JSON file.
    
    Args:
        content_id: Unique content identifier
        decision: Decision results dictionary
        
    Returns:
        Path to saved decision file
    """
    decision_path = settings.decisions_dir / f"{content_id}.json"
    
    # Add timestamp
    if "decision_timestamp" not in decision:
        decision["decision_timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    decision["content_id"] = content_id
    
    with open(decision_path, "w", encoding="utf-8") as f:
        json.dump(decision, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved decision for content_id={content_id}")
    return decision_path


def load_decision(content_id: str) -> Optional[Dict[str, Any]]:
    """Load decision results from JSON file.
    
    Args:
        content_id: Unique content identifier
        
    Returns:
        Decision dictionary or None if not found
    """
    decision_path = settings.decisions_dir / f"{content_id}.json"
    
    if not decision_path.exists():
        logger.warning(f"Decision not found for content_id={content_id}")
        return None
    
    with open(decision_path, "r", encoding="utf-8") as f:
        return json.load(f)


def append_audit_log(event: Dict[str, Any]) -> None:
    """Append event to audit log (JSONL format).
    
    Args:
        event: Event dictionary to log
    """
    # Get current date for daily log files
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    date_dir = settings.audit_dir / date_str
    date_dir.mkdir(parents=True, exist_ok=True)
    
    audit_file = date_dir / "events.jsonl"
    
    # Add timestamp if not present
    if "timestamp" not in event:
        event["timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    # Append as JSON line
    with open(audit_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def get_content_path(content_id: str, user_id: str) -> Path:
    """Get the content directory path.
    
    Args:
        content_id: Unique content identifier
        user_id: User identifier
        
    Returns:
        Path to content directory
    """
    return settings.content_dir / user_id / content_id


def get_frames_dir(content_id: str, user_id: str) -> Path:
    """Get the frames directory path.
    
    Args:
        content_id: Unique content identifier
        user_id: User identifier
        
    Returns:
        Path to frames directory
    """
    frames_dir = get_content_path(content_id, user_id) / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    return frames_dir
