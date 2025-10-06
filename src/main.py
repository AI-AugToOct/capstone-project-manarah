"""Main API routes for Manarah backend."""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import tempfile
import shutil
import logging
from typing import Optional
from datetime import datetime
import uvicorn
import os


from src.config import settings
from src.storage import (
    save_metadata, load_metadata, save_analysis, load_analysis,
    save_decision, load_decision, append_audit_log, update_metadata
)
from src.preprocessor import ContentPreprocessor
from src.vision_analyzer import VisionAnalyzer
from src.text_analyzer import TextAnalyzer
from src.decision_engine import DecisionEngine

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Manarah Content Moderation API",
    description="AI-powered content moderation for Saudi social media",
    version="1.0.0"
)

# Add CORS middleware for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # React default
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Manarah Content Moderation API",
        "status": "running",
        "version": "1.0.0"
    }


async def process_content_async(content_id: str, user_id: str, content_type: str):
    """Background task to process content analysis.
    
    Args:
        content_id: Content identifier
        user_id: User identifier
        content_type: "video" or "image"
    """
    try:
        logger.info(f"Starting analysis for content_id={content_id}")
        
        # Load metadata
        metadata = load_metadata(content_id, user_id)
        if not metadata:
            logger.error(f"Metadata not found for content_id={content_id}")
            return
        
        # Vision Analysis
        vision_analysis = {}
        if content_type == "video":
            frame_paths = [Path(p) for p in metadata["file_paths"].get("frames", [])]
            # Sample every 3rd frame to reduce API costs (5 fps effective)
            vision_analysis = VisionAnalyzer.analyze_frames(frame_paths, sample_rate=3)
        else:  # image
            original_path = Path(metadata["file_paths"]["original"])
            vision_analysis = VisionAnalyzer.analyze_image(original_path)
        
        # Text Analysis
        audio_path = None
        if content_type == "video" and metadata["file_paths"].get("audio"):
            audio_path = Path(metadata["file_paths"]["audio"])
        
        caption = metadata.get("post_caption", "")
        text_analysis = TextAnalyzer.analyze_content_text(audio_path, caption)
        
        # Save analysis results
        analysis_results = {
            "content_id": content_id,
            "vision_analysis": vision_analysis,
            "text_analysis": text_analysis
        }
        save_analysis(content_id, analysis_results)
        
        # Log audit event
        append_audit_log({
            "event": "analysis_complete",
            "content_id": content_id,
            "vision_score": vision_analysis.get("avg_violation_score", vision_analysis.get("violation_score", 0)),
            "text_score": text_analysis.get("violation_score", 0)
        })
        
        # Make Decision
        decision = DecisionEngine.make_decision(
            vision_analysis, text_analysis, content_type
        )
        save_decision(content_id, decision)
        
        # Update metadata status
        update_metadata(content_id, user_id, {"status": "completed"})
        
        # Log audit event
        append_audit_log({
            "event": "decision_made",
            "content_id": content_id,
            "action": decision["action"],
            "score": decision["combined_score"]
        })
        
        logger.info(f"Analysis completed for content_id={content_id}, action={decision['action']}")
        
    except Exception as e:
        logger.error(f"Processing failed for content_id={content_id}: {e}", exc_info=True)
        # Update status to failed
        try:
            update_metadata(content_id, user_id, {"status": "failed", "error": str(e)})
        except:
            pass


@app.post("/api/v1/content/upload")
async def upload_content(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    caption: Optional[str] = Form(None)
):
    """Upload content for moderation analysis.
    
    Args:
        file: Video or image file
        user_id: User identifier
        caption: Optional post caption
        
    Returns:
        Content ID and processing status
    """
    try:
        # Validate file size
        file_size_mb = 0
        if file.size:
            file_size_mb = file.size / (1024 * 1024)
        
        max_size = settings.max_upload_size_mb
        if file_size_mb > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {max_size}MB"
            )
        
        # Validate file type
        allowed_extensions = [".mp4", ".mov", ".avi", ".jpg", ".jpeg", ".png", ".webp"]
        
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required"
            )
        
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = Path(temp_file.name)
        
        try:
            # Process upload
            content_id, content_type, metadata = ContentPreprocessor.process_upload(
                temp_path, user_id, caption
            )
            
            # Schedule background processing
            background_tasks.add_task(
                process_content_async, content_id, user_id, content_type
            )
            
            logger.info(f"Upload successful: content_id={content_id}, user_id={user_id}")
            
            return JSONResponse(
                status_code=202,  # 202 Accepted for async processing
                content={
                    "content_id": content_id,
                    "status": "processing",
                    "message": "Content uploaded successfully and queued for analysis"
                }
            )
            
        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/v1/content/{content_id}/status")
async def get_content_status(content_id: str, user_id: str):
    """Get processing status for content.
    
    Args:
        content_id: Content identifier
        user_id: User identifier (for validation)
        
    Returns:
        Processing status and decision if completed
    """
    try:
        # Load metadata
        metadata = load_metadata(content_id, user_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Content not found")
        
        status = metadata.get("status", "unknown")
        
        response = {
            "content_id": content_id,
            "status": status,
            "uploaded_at": metadata.get("upload_timestamp")
        }
        
        # If completed, include decision
        if status == "completed":
            decision = load_decision(content_id)
            if decision:
                response["decision"] = {
                    "action": decision.get("action"),
                    "score": decision.get("combined_score"),
                    "reason": decision.get("reasoning")
                }
                response["processed_at"] = decision.get("decision_timestamp")
        
        elif status == "failed":
            response["error"] = metadata.get("error", "Processing failed")
        
        return JSONResponse(status_code=200, content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/content/{content_id}/details")
async def get_content_details(content_id: str, user_id: str):
    """Get detailed analysis results for content.
    
    Args:
        content_id: Content identifier
        user_id: User identifier (for validation)
        
    Returns:
        Complete analysis and decision details
    """
    try:
        # Load all data
        metadata = load_metadata(content_id, user_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Content not found")
        
        analysis = load_analysis(content_id)
        decision = load_decision(content_id)
        
        if not analysis or not decision:
            raise HTTPException(
                status_code=404,
                detail="Analysis not completed yet. Check /status endpoint."
            )
        
        # Build response
        response = {
            "content_id": content_id,
            "content_type": metadata.get("content_type"),
            "status": metadata.get("status"),
            "uploaded_at": metadata.get("upload_timestamp"),
            "vision_analysis": analysis.get("vision_analysis", {}),
            "text_analysis": analysis.get("text_analysis", {}),
            "decision": decision,
            "evidence": {
                "original_file": metadata["file_paths"].get("original"),
                "frames": metadata["file_paths"].get("frames", [])[:5],  # First 5 frames
                "audio": metadata["file_paths"].get("audio"),
                "metadata": f"data/content/{user_id}/{content_id}/metadata.json"
            }
        }
        
        return JSONResponse(status_code=200, content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Details retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port)
