"""Content preprocessing module for frame and audio extraction."""
import uuid
import shutil
import logging
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
import ffmpeg
from PIL import Image

from src.config import settings
from src.storage import (
    save_metadata, 
    get_content_path, 
    get_frames_dir,
    append_audit_log
)

logger = logging.getLogger(__name__)


class ContentPreprocessor:
    """Handles video/image upload and preprocessing."""
    
    @staticmethod
    def process_upload(
        file_path: Path,
        user_id: str,
        caption: Optional[str] = None
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Process uploaded content (video or image).
        
        Args:
            file_path: Path to uploaded file
            user_id: User identifier
            caption: Optional caption text
            
        Returns:
            Tuple of (content_id, content_type, metadata)
        """
        content_id = str(uuid.uuid4())
        
        # Determine content type
        content_type = ContentPreprocessor._get_content_type(file_path)
        
        # Create content directory
        content_dir = get_content_path(content_id, user_id)
        content_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy original file
        file_extension = file_path.suffix.lower()
        original_path = content_dir / f"original{file_extension}"
        shutil.copy(file_path, original_path)
        
        logger.info(f"Processing upload: content_id={content_id}, type={content_type}")
        
        # Initialize metadata
        metadata = {
            "content_id": content_id,
            "user_id": user_id,
            "content_type": content_type,
            "status": "processing",
            "post_caption": caption or "",
            "file_paths": {
                "original": str(original_path)
            }
        }
        
        # Process based on type
        if content_type == "video":
            metadata.update(ContentPreprocessor._process_video(
                original_path, content_id, user_id
            ))
        else:  # image
            metadata.update(ContentPreprocessor._process_image(original_path))
        
        # Save metadata
        save_metadata(content_id, user_id, metadata)
        
        # Log audit event
        append_audit_log({
            "event": "upload",
            "content_id": content_id,
            "user_id": user_id,
            "content_type": content_type
        })
        
        logger.info(f"Upload processed successfully: content_id={content_id}")
        return content_id, content_type, metadata
    
    @staticmethod
    def _get_content_type(file_path: Path) -> str:
        """Determine content type from file extension."""
        extension = file_path.suffix.lower()
        video_extensions = [".mp4", ".mov", ".avi"]
        image_extensions = [".jpg", ".jpeg", ".png", ".webp"]
        
        if extension in video_extensions:
            return "video"
        elif extension in image_extensions:
            return "image"
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    @staticmethod
    def _process_video(
        video_path: Path,
        content_id: str,
        user_id: str
    ) -> dict:
        """Extract frames and audio from video.
        
        Args:
            video_path: Path to video file
            content_id: Content identifier
            user_id: User identifier
            
        Returns:
            Dictionary with video metadata
        """
        try:
            # Get video info
            probe = ffmpeg.probe(str(video_path))
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            duration = float(probe['format']['duration'])
            fps = settings.frame_extraction_fps
            
            # Extract frames
            frames_dir = get_frames_dir(content_id, user_id)
            frame_paths = ContentPreprocessor._extract_frames(
                video_path, frames_dir, fps
            )
            
            # Extract audio
            audio_path = get_content_path(content_id, user_id) / "audio.wav"
            ContentPreprocessor._extract_audio(video_path, audio_path)
            
            logger.info(
                f"Video processed: {len(frame_paths)} frames extracted at {fps} fps"
            )
            
            return {
                "duration_seconds": duration,
                "frame_count": len(frame_paths),
                "fps": fps,
                "file_paths": {
                    "frames": [str(p) for p in frame_paths],
                    "audio": str(audio_path) if audio_path.exists() else None
                }
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            raise
    
    @staticmethod
    def _extract_frames(
        video_path: Path,
        output_dir: Path,
        fps: int
    ) -> List[Path]:
        """Extract frames from video at specified FPS.
        
        Args:
            video_path: Path to video file
            output_dir: Directory to save frames
            fps: Frames per second to extract
            
        Returns:
            List of frame file paths
        """
        try:
            # Use ffmpeg to extract frames
            (
                ffmpeg
                .input(str(video_path))
                .filter('fps', fps=fps)
                .output(
                    str(output_dir / 'frame_%04d.jpg'),
                    format='image2',
                    vcodec='mjpeg',
                    qscale=2  # High quality
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # Get list of extracted frames
            frame_paths = sorted(output_dir.glob('frame_*.jpg'))
            return frame_paths
            
        except ffmpeg.Error as e:
            logger.error(f"Frame extraction failed: {e.stderr.decode()}")
            raise
    
    @staticmethod
    def _extract_audio(video_path: Path, output_path: Path) -> None:
        """Extract audio track from video.
        
        Args:
            video_path: Path to video file
            output_path: Path to save audio file
        """
        try:
            (
                ffmpeg
                .input(str(video_path))
                .output(
                    str(output_path),
                    acodec='pcm_s16le',  # WAV format
                    ar='16000',  # 16kHz sample rate for Whisper
                    ac=1  # Mono
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            logger.info(f"Audio extracted to {output_path}")
            
        except ffmpeg.Error as e:
            # Some videos may not have audio - log but don't fail
            logger.warning(f"Audio extraction failed (video may have no audio): {e.stderr.decode()}")
    
    @staticmethod
    def _process_image(image_path: Path) -> dict:
        """Process image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with image metadata
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
            
            return {
                "width": width,
                "height": height
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise

