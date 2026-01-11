from typing import Dict, Any, List
from .forms import FormDetector

class ResumeAutofill:
    """
    Maps resume data to identified form fields.
    """
    
    def __init__(self, resume_data: Dict[str, Any]):
        self.data = resume_data
        
    def map_field(self, field_meta: Dict[str, Any]) -> str:
        """
        Returns the value to fill for a given field based on heuristics.
        """
        label = field_meta.get("label", "")
        name = field_meta.get("name", "")
        field_type = field_meta.get("type", "")
        
        # Combine label and name for keyword search
        key = f"{label} {name}".lower()
        
        # Direct Mapping Heuristics
        if "first name" in key:
            return self.data.get("first_name", "")
        elif "last name" in key:
            return self.data.get("last_name", "")
        elif "email" in key:
            return self.data.get("email", "")
        elif "phone" in key or "mobile" in key:
            return self.data.get("phone", "")
        elif "linkedin" in key:
            return self.data.get("linkedin_url", "")
        elif "github" in key:
            return self.data.get("github_url", "")
        elif "portfolio" in key or "website" in key:
            return self.data.get("portfolio_url", "")
        
        # Cover Letter
        if "cover letter" in key:
            return self.data.get("cover_letter", "")
            
        return None
