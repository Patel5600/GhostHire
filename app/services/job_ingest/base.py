from abc import ABC, abstractmethod
from typing import List, Dict, Any

class JobSourceBase(ABC):
    """Abstract base class for all job sources (Scrapers, APIs, FeedParsers)."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        """
        Fetch raw job data from the source.
        Returns a list of raw dictionaries.
        """
        pass

    @abstractmethod
    async def validate_config(self) -> bool:
        """Validate if the provided configuration is sufficient."""
        pass
