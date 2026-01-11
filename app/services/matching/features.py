import re
from typing import Set, List

class FeatureExtractor:
    """
    Extracts structured features from raw text.
    """
    
    def __init__(self):
        # In production, load this from a DB or large JSON file
        self.common_skills = {
            "python", "java", "c++", "javascript", "typescript", "react", "angular", "vue",
            "docker", "kubernetes", "aws", "gcp", "azure", "sql", "nosql", "redis",
            "machine learning", "ai", "nlp", "pytorch", "tensorflow", "scikit-learn",
            "fastapi", "flask", "django", "git", "ci/cd", "agile", "scrum"
        }
        
    def extract_skills(self, text: str) -> Set[str]:
        if not text:
            return set()
            
        found = set()
        text_lower = text.lower()
        
        # Simple keyword matching
        for skill in self.common_skills:
            # Boundary check to avoid substrings (e.g., "java" in "javascript")
            # Using regex for word boundaries
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found.add(skill)
                
        return found
    
    def extract_keywords(self, text: str) -> List[str]:
        if not text:
            return []
        # Basic tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        # Remove stopwords (simplified list)
        stopwords = {"and", "the", "to", "of", "in", "a", "for", "with", "on", "as", "is", "an", "or"}
        return [w for w in words if w not in stopwords and len(w) > 2]
