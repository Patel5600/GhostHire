from typing import Dict, Any, Optional
from pydantic import BaseModel

class IngestTriggerRequest(BaseModel):
    source_name: str
    source_type: str # 'api', 'scraper'
    base_url: str
    config: Dict[str, Any]
    force_rescan: bool = False

class IngestStatus(BaseModel):
    task_id: str
    status: str
