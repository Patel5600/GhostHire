from typing import Dict, Any, Set

class WeightedRanker:
    """
    Scoring engine that combines multiple signals.
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "skills_overlap": 0.5,
            "text_similarity": 0.3,
            "experience_match": 0.2
        }
        
    def score(self, 
              skills_resume: Set[str], skills_job: Set[str], 
              text_similarity: float) -> Dict[str, Any]:
              
        # 1. Skill Score (Jaccard Index)
        union = len(skills_resume | skills_job)
        intersection = len(skills_resume & skills_job)
        skill_score = (intersection / union) if union > 0 else 0.0
        
        # 2. Text Similarity (Already provided 0-1)
        
        # 3. Final Weighted Score
        final_score = (
            (skill_score * self.weights["skills_overlap"]) +
            (text_similarity * self.weights["text_similarity"])
        )
        
        # Normalize to 0-100
        final_score_scaled = min(100.0, max(0.0, final_score * 100)) # Simple scaling strategy
        
        # Identify Gaps/Strengths
        strengths = list(skills_resume & skills_job)
        gaps = list(skills_job - skills_resume)
        
        return {
            "total_score": round(final_score_scaled, 2),
            "breakdown": {
                "skill_score": round(skill_score, 2),
                "text_similarity": round(text_similarity, 2)
            },
            "strengths": strengths,
            "gaps": gaps,
            "recommendation": self._get_recommendation(final_score_scaled)
        }

    def _get_recommendation(self, score: float) -> str:
        if score >= 80:
            return "Strong Match"
        elif score >= 50:
            return "Potential Match"
        else:
            return "Weak Match"
