"""Vision analysis module using GPT-4o."""
import base64
import logging
import json
from pathlib import Path
from typing import List, Dict, Any
import openai
from openai import OpenAI

from src.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)


# Comprehensive vision analysis prompt
VISION_ANALYSIS_PROMPT = """You are an expert content moderator analyzing images for violations in Saudi social media content.

Analyze this image for the following violation categories:

**1. BULLYING & MOCKERY (التنمر والاستهزاء)**
- Offensive hand gestures (middle finger, rude signs)
- Mocking facial expressions toward camera
- Insulting text overlays on images
- Screenshots of harassment messages

**2. CHILD EXPLOITATION (استغلال الأطفال)**
PROHIBITED indicators:
- Child occupies >40% of frame
- Child performing for camera (challenges, reactions)
- Child looking directly at camera (performing)
- Close-up face framing (thumbnail bait)
- Text overlays mentioning child
- Professional lighting focused on child

ALLOWED:
- Child in background (<20% frame time)
- Child incidentally in public space
- Educational content (child learning, not performing)

**3. WORKER EXPLOITATION (استغلال العاملين)**
- Domestic worker facing camera (not natural work position)
- Worker performing for content
- Workers in staged scenarios

**4. VULGAR LANGUAGE (الألفاظ المبتذلة)**
- Profanity in text overlays
- Censored text (***) indicating hidden words
- Obscene symbols

**5. WEALTH BRAGGING (التباهي بالأموال)**
- Cash stacks prominently displayed
- Saudi Riyal notes spread out
- Luxury watches showcased (Rolex, AP)
- Multiple expensive cars in frame
- Designer tags visible
- Jewelry display
- High-end property tours

**6. TRIBAL INCITEMENT (إثارة القبلية)**
- Tribal flags prominently displayed
- Tribal symbols/insignia
- Maps showing tribal territories

**7. SECTARIAN CONTENT (إثارة الطائفية)**
- Sectarian symbols
- Divisive religious flags

**8. RACISM (العنصرية)**
- Racist symbols (swastikas)
- Mocking ethnic imagery
- Blackface or ethnic mockery

Return a JSON response with this exact structure:
{
  "violations": [
    {
      "category": "child_exploitation|bullying|worker_exploitation|vulgar_language|wealth_bragging|tribal|sectarian|racism",
      "confidence": 0.0-1.0,
      "description": "detailed description of what was detected",
      "evidence": "specific visual elements observed",
      "severity": "low|medium|high"
    }
  ],
  "violation_score": 0.0-1.0,
  "overall_assessment": "brief summary"
}

If no violations detected, return {"violations": [], "violation_score": 0.0, "overall_assessment": "No violations detected"}.
Be precise and culturally aware. Consider Saudi Arabian context."""


class VisionAnalyzer:
    """Analyzes images/frames for visual violations using GPT-4o."""
    
    @staticmethod
    def analyze_frame(frame_path: Path) -> Dict[str, Any]:
        """Analyze a single frame for violations.
        
        Args:
            frame_path: Path to image file
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Encode image to base64
            with open(frame_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Call GPT-4o Vision API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": VISION_ANALYSIS_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2  # Low temperature for consistent results
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            
            # Ensure we have content
            if not result_text:
                logger.warning("Empty response from GPT-4o")
                return {
                    "violations": [],
                    "violation_score": 0.0,
                    "overall_assessment": "",
                    "parse_error": True
                }
            
            # Try to parse as JSON
            
            # Strip markdown code blocks if present
            if result_text.strip().startswith("```"):
                # Remove ```json or ``` at start
                result_text = result_text.strip()
                if result_text.startswith("```json"):
                    result_text = result_text[7:]  # Remove ```json
                elif result_text.startswith("```"):
                    result_text = result_text[3:]  # Remove ```
                
                # Remove closing ```
                if result_text.endswith("```"):
                    result_text = result_text[:-3]
                
                result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            logger.info(f"Frame analyzed: {frame_path.name}, score={result.get('violation_score', 0)}")
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            safe_text = result_text if 'result_text' in locals() and result_text else 'Unknown'
            logger.warning(f"Raw response: {safe_text[:200]}...")
            # Fallback: extract score and return basic structure
            return {
                "violations": [],
                "violation_score": 0.0,
                "overall_assessment": safe_text if safe_text != 'Unknown' else "",
                "parse_error": True
            }
        except Exception as e:
            logger.error(f"Frame analysis failed: {e}")
            raise
    
    @staticmethod
    def analyze_frames(frame_paths: List[Path], sample_rate: int = 1) -> Dict[str, Any]:
        """Analyze multiple frames from a video.
        
        Args:
            frame_paths: List of frame file paths
            sample_rate: Analyze every Nth frame (1 = all frames)
            
        Returns:
            Aggregated analysis results
        """
        if not frame_paths:
            return {
                "frames_analyzed": 0,
                "avg_violation_score": 0.0,
                "violations": [],
                "error": "No frames to analyze"
            }
        
        # Sample frames
        sampled_frames = frame_paths[::sample_rate]
        logger.info(f"Analyzing {len(sampled_frames)} frames (sample rate: {sample_rate})")
        
        all_violations = []
        total_score = 0.0
        analyzed_count = 0
        
        for idx, frame_path in enumerate(sampled_frames):
            try:
                frame_num = idx * sample_rate + 1
                result = VisionAnalyzer.analyze_frame(frame_path)
                
                # Add frame number to violations
                for violation in result.get("violations", []):
                    violation["frame_number"] = frame_num
                    all_violations.append(violation)
                
                total_score += result.get("violation_score", 0.0)
                analyzed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to analyze frame {frame_num}: {e}")
                continue
        
        # Calculate average score
        avg_score = total_score / analyzed_count if analyzed_count > 0 else 0.0
        
        # Sort violations by confidence (highest first)
        all_violations.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return {
            "frames_analyzed": analyzed_count,
            "total_frames": len(frame_paths),
            "sample_rate": sample_rate,
            "avg_violation_score": round(avg_score, 3),
            "violations": all_violations[:20],  # Top 20 violations
            "max_violation_score": max(
                [v.get("confidence", 0) for v in all_violations],
                default=0.0
            )
        }
    
    @staticmethod
    def analyze_image(image_path: Path) -> Dict[str, Any]:
        """Analyze a single image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Analysis results
        """
        result = VisionAnalyzer.analyze_frame(image_path)
        
        return {
            "image_analyzed": True,
            "violation_score": result.get("violation_score", 0.0),
            "violations": result.get("violations", []),
            "overall_assessment": result.get("overall_assessment", "")
        }
