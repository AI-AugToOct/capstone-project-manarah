"""Decision engine for content moderation actions."""
import logging
from typing import Dict, Any, List, Tuple

from src.config import settings

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Makes moderation decisions based on analysis results."""
    
    # Action thresholds
    AUTO_REMOVE_THRESHOLD = settings.auto_remove_threshold
    REVIEW_THRESHOLD = settings.review_threshold
    WARNING_THRESHOLD = settings.warning_threshold
    
    # Weights for scoring
    VISION_WEIGHT_VIDEO = 0.6
    TEXT_WEIGHT_VIDEO = 0.4
    VISION_WEIGHT_IMAGE = 0.7
    TEXT_WEIGHT_IMAGE = 0.3
    
    @staticmethod
    def make_decision(
        vision_analysis: Dict[str, Any],
        text_analysis: Dict[str, Any],
        content_type: str
    ) -> Dict[str, Any]:
        """Make moderation decision based on analysis results.
        
        Args:
            vision_analysis: Results from vision analyzer
            text_analysis: Results from text analyzer
            content_type: "video" or "image"
            
        Returns:
            Decision dictionary with action and reasoning
        """
        # Extract scores
        vision_score = vision_analysis.get("avg_violation_score", 0.0) if content_type == "video" else vision_analysis.get("violation_score", 0.0)
        text_score = text_analysis.get("violation_score", 0.0)
        
        # Calculate combined score based on content type
        if content_type == "video":
            combined_score = (
                vision_score * DecisionEngine.VISION_WEIGHT_VIDEO +
                text_score * DecisionEngine.TEXT_WEIGHT_VIDEO
            )
        else:  # image
            combined_score = (
                vision_score * DecisionEngine.VISION_WEIGHT_IMAGE +
                text_score * DecisionEngine.TEXT_WEIGHT_IMAGE
            )
        
        # Check for hard rules
        hard_rule = DecisionEngine._check_hard_rules(
            vision_analysis, text_analysis, vision_score, text_score
        )
        
        # Determine action
        if hard_rule:
            action, reasoning = hard_rule
            priority = "critical"
        else:
            action, reasoning, priority = DecisionEngine._determine_action(combined_score)
        
        # Get violation summary
        violation_summary = DecisionEngine._get_violation_summary(
            vision_analysis, text_analysis
        )
        
        decision = {
            "vision_score": round(vision_score, 3),
            "text_score": round(text_score, 3),
            "combined_score": round(combined_score, 3),
            "action": action,
            "hard_rule_triggered": hard_rule[0] if hard_rule else None,
            "reasoning": reasoning,
            "priority": priority,
            "evidence_summary": violation_summary
        }
        
        logger.info(
            f"Decision made: action={action}, score={combined_score:.3f}, "
            f"hard_rule={hard_rule[0] if hard_rule else None}"
        )
        
        return decision
    
    @staticmethod
    def _check_hard_rules(
        vision_analysis: Dict[str, Any],
        text_analysis: Dict[str, Any],
        vision_score: float,
        text_score: float
    ) -> Tuple[str, str] | None:
        """Check if any hard rules apply (override scoring).
        
        Args:
            vision_analysis: Vision analysis results
            text_analysis: Text analysis results
            vision_score: Vision violation score
            text_score: Text violation score
            
        Returns:
            Tuple of (action, reasoning) if rule triggered, None otherwise
        """
        vision_violations = vision_analysis.get("violations", [])
        text_violations = text_analysis.get("violations", [])
        
        # Hard Rule 1: Child exploitation with high confidence → Force human review
        for v in vision_violations + text_violations:
            if v.get("category") == "child_exploitation" and v.get("confidence", 0) > 0.80:
                return ("human_review", "Child exploitation detected with high confidence - requires manual review")
        
        # Hard Rule 2: Hate symbols with very high confidence → Auto-remove
        for v in vision_violations:
            if v.get("category") in ["racism", "sectarian"] and v.get("confidence", 0) > 0.90:
                if "symbol" in v.get("description", "").lower() or "flag" in v.get("description", "").lower():
                    return ("auto_remove", "Hate symbols detected with very high confidence")
        
        # Hard Rule 3: Multiple violations with high confidence → Force review
        high_confidence_violations = [
            v for v in vision_violations + text_violations
            if v.get("confidence", 0) > 0.85
        ]
        
        if len(high_confidence_violations) >= 2:
            categories = set(v.get("category") for v in high_confidence_violations)
            return (
                "human_review",
                f"Multiple high-confidence violations detected: {', '.join(categories)}"
            )
        
        return None
    
    @staticmethod
    def _determine_action(score: float) -> Tuple[str, str, str]:
        """Determine action based on combined score.
        
        Args:
            score: Combined violation score
            
        Returns:
            Tuple of (action, reasoning, priority)
        """
        if score >= DecisionEngine.AUTO_REMOVE_THRESHOLD:
            return (
                "auto_remove",
                f"High violation score ({score:.2f}) exceeds auto-remove threshold",
                "high"
            )
        elif score >= DecisionEngine.REVIEW_THRESHOLD:
            return (
                "human_review",
                f"Medium violation score ({score:.2f}) requires human review",
                "medium"
            )
        elif score >= DecisionEngine.WARNING_THRESHOLD:
            return (
                "warning",
                f"Low violation score ({score:.2f}) - issue warning to user",
                "low"
            )
        else:
            return (
                "allow",
                f"Violation score ({score:.2f}) below warning threshold",
                "none"
            )
    
    @staticmethod
    def _get_violation_summary(
        vision_analysis: Dict[str, Any],
        text_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate summary of detected violations.
        
        Args:
            vision_analysis: Vision analysis results
            text_analysis: Text analysis results
            
        Returns:
            Violation summary dictionary
        """
        vision_violations = vision_analysis.get("violations", [])
        text_violations = text_analysis.get("violations", [])
        
        all_violations = vision_violations + text_violations
        
        # Get unique categories
        categories = list(set(v.get("category") for v in all_violations if v.get("category")))
        
        # Find highest confidence
        highest_confidence = max(
            [v.get("confidence", 0) for v in all_violations],
            default=0.0
        )
        
        # Count by severity
        severity_counts = {
            "high": len([v for v in all_violations if v.get("severity") == "high"]),
            "medium": len([v for v in all_violations if v.get("severity") == "medium"]),
            "low": len([v for v in all_violations if v.get("severity") == "low"])
        }
        
        return {
            "total_violations": len(all_violations),
            "categories": categories,
            "highest_confidence": round(highest_confidence, 3),
            "severity_breakdown": severity_counts,
            "vision_violations": len(vision_violations),
            "text_violations": len(text_violations)
        }
