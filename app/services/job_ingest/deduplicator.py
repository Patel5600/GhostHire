import hashlib
from typing import Dict, Any

class JobDeduplicator:
    """Handles logic for detecting unique jobs."""

    def generate_hash(self, valid_job_data: Dict[str, Any]) -> str:
        """
        Create a deterministic hash based on core identity fields.
        Using Title + Company + Location (normalized).
        """
        title = (valid_job_data.get("title") or "").lower().strip()
        company = (valid_job_data.get("company") or "").lower().strip()
        location = (valid_job_data.get("location") or "").lower().strip()
        
        # We can also use URL if that's preferred, but URLs often change with query params.
        # Fallback to URL if core fields are missing?
        
        raw_string = f"{title}|{company}|{location}"
        return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
