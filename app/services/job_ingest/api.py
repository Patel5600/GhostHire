from typing import List, Dict, Any
import httpx
from .base import JobSourceBase

class APIJobSource(JobSourceBase):
    """Generic API scraper."""
    
    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        url = self.config.get("url")
        headers = self.config.get("headers", {})
        params = self.config.get("params", {})
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            # Allow config to specify where the list is located (e.g., 'results' or 'jobs')
            list_key = self.config.get("list_key")
            if list_key and list_key in data:
                return data[list_key]
            elif isinstance(data, list):
                return data
            return []

    async def validate_config(self) -> bool:
        return "url" in self.config
