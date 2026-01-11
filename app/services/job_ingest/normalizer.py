from typing import Dict, Any, List, Optional
import re

class JobNormalizer:
    """Normalizes raw job data into structured format."""

    def normalize(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Process a raw job dictionary and return cleaner data."""
        title = raw_job.get("title", "").strip()
        company = raw_job.get("company", "").strip()
        location = raw_job.get("location", "").strip()
        description = raw_job.get("description", "")
        
        salary_min, salary_max, currency = self._extract_salary(raw_job.get("salary_text", "") or description)
        tags = self._extract_tags(description)
        is_remote = self._check_remote(location, description)

        return {
            "title": title,
            "company": company,
            "location": location,
            "url": raw_job.get("url"),
            "description": description,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "currency": currency,
            "tags": tags,
            "is_remote": is_remote,
            "raw_data": raw_job
        }

    def _extract_salary(self, text: str) -> tuple[Optional[float], Optional[float], Optional[str]]:
        """Simple regex-based salary extraction."""
        # This is a basic implementation. In production, use NLP or rigorous regex patterns.
        if not text:
            return None, None, None
            
        # Look for patterns like $50k - $80k or $50,000
        # Very simplified for this example
        match = re.search(r'\$(\d{2,3})k', text, re.IGNORECASE)
        if match:
             val = float(match.group(1)) * 1000
             return val, val, "USD"
        
        return None, None, None

    def _extract_tags(self, description: str) -> List[str]:
        """Extract tech stack tags from description."""
        common_tags = ["python", "java", "react", "fastapi", "docker", "kubernetes", "aws", "sql"]
        found = []
        if not description:
            return found
            
        desc_lower = description.lower()
        for tag in common_tags:
            if tag in desc_lower:
                found.append(tag)
        return found

    def _check_remote(self, location: str, description: str) -> bool:
        """Detect if job is remote."""
        keywords = ["remote", "work from home", "wfh"]
        text = (location + " " + description).lower()
        return any(k in text for k in keywords)
