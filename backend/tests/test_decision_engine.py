"""Basic unit tests for Manarah components."""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.decision_engine import DecisionEngine


class TestDecisionEngine:
    """Test the decision engine logic."""
    
    def test_video_scoring(self):
        """Test video scoring formula."""
        vision_analysis = {"avg_violation_score": 0.8, "violations": []}
        text_analysis = {"violation_score": 0.6, "violations": []}
        
        decision = DecisionEngine.make_decision(
            vision_analysis, text_analysis, "video"
        )
        
        # Expected: (0.8 * 0.6) + (0.6 * 0.4) = 0.48 + 0.24 = 0.72
        assert decision["combined_score"] == pytest.approx(0.72, 0.01)
        assert decision["action"] == "human_review"
    
    def test_image_scoring(self):
        """Test image scoring formula."""
        vision_analysis = {"violation_score": 0.9, "violations": []}
        text_analysis = {"violation_score": 0.5, "violations": []}
        
        decision = DecisionEngine.make_decision(
            vision_analysis, text_analysis, "image"
        )
        
        # Expected: (0.9 * 0.7) + (0.5 * 0.3) = 0.63 + 0.15 = 0.78
        assert decision["combined_score"] == pytest.approx(0.78, 0.01)
        assert decision["action"] == "human_review"
    
    def test_auto_remove_threshold(self):
        """Test auto-remove threshold."""
        vision_analysis = {"avg_violation_score": 0.9, "violations": []}
        text_analysis = {"violation_score": 0.8, "violations": []}
        
        decision = DecisionEngine.make_decision(
            vision_analysis, text_analysis, "video"
        )
        
        # Score should be >= 0.85
        assert decision["combined_score"] >= 0.85
        assert decision["action"] == "auto_remove"
    
    def test_allow_threshold(self):
        """Test allow threshold."""
        vision_analysis = {"avg_violation_score": 0.2, "violations": []}
        text_analysis = {"violation_score": 0.1, "violations": []}
        
        decision = DecisionEngine.make_decision(
            vision_analysis, text_analysis, "video"
        )
        
        # Score should be < 0.40
        assert decision["combined_score"] < 0.40
        assert decision["action"] == "allow"
    
    def test_child_exploitation_hard_rule(self):
        """Test child exploitation hard rule."""
        vision_analysis = {
            "avg_violation_score": 0.5,
            "violations": [
                {
                    "category": "child_exploitation",
                    "confidence": 0.85,
                    "description": "Child as main subject"
                }
            ]
        }
        text_analysis = {"violation_score": 0.3, "violations": []}
        
        decision = DecisionEngine.make_decision(
            vision_analysis, text_analysis, "video"
        )
        
        # Should trigger hard rule
        assert decision["action"] == "human_review"
        assert decision["hard_rule_triggered"] is not None
    
    def test_multiple_violations_hard_rule(self):
        """Test multiple violations hard rule."""
        vision_analysis = {
            "avg_violation_score": 0.6,
            "violations": [
                {"category": "bullying", "confidence": 0.87},
                {"category": "wealth_bragging", "confidence": 0.86}
            ]
        }
        text_analysis = {"violation_score": 0.5, "violations": []}
        
        decision = DecisionEngine.make_decision(
            vision_analysis, text_analysis, "video"
        )
        
        # Should trigger hard rule for multiple high-confidence violations
        assert decision["action"] == "human_review"
        assert decision["hard_rule_triggered"] is not None


class TestViolationSummary:
    """Test violation summary generation."""
    
    def test_summary_generation(self):
        """Test that violation summary is generated correctly."""
        vision_analysis = {
            "violations": [
                {"category": "bullying", "confidence": 0.8, "severity": "high"},
                {"category": "vulgar_language", "confidence": 0.6, "severity": "medium"}
            ]
        }
        text_analysis = {
            "violations": [
                {"category": "wealth_bragging", "confidence": 0.7, "severity": "low"}
            ]
        }
        
        decision = DecisionEngine.make_decision(
            vision_analysis, text_analysis, "video"
        )
        
        summary = decision["evidence_summary"]
        
        assert summary["total_violations"] == 3
        assert "bullying" in summary["categories"]
        assert "wealth_bragging" in summary["categories"]
        assert summary["highest_confidence"] == 0.8
        assert summary["severity_breakdown"]["high"] == 1
        assert summary["severity_breakdown"]["medium"] == 1
        assert summary["severity_breakdown"]["low"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
