from typing import Dict, Any, Type
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime
import time

from app.models.job import Job, JobSource, IngestionLog
from .base import JobSourceBase
from .api import APIJobSource
from .scraper import PlaywrightScraper
from .normalizer import JobNormalizer
from .deduplicator import JobDeduplicator

class IngestPipeline:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.normalizer = JobNormalizer()
        self.deduplicator = JobDeduplicator()

    async def run(self, source_id: int):
        """
        Executes the full ingestion pipeline for a given valid Source ID.
        """
        start_time = time.time()
        
        # 1. Load Source Config
        source = await self.session.get(JobSource, source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")
            
        # 2. Initialize Strategy
        strategy = self._get_strategy(source)
        if not await strategy.validate_config():
            await self._log_result(source, "failed", error="Invalid Config")
            return
            
        try:
            # 3. Fetch
            raw_jobs = await strategy.fetch_jobs()
            
            dedup_count = 0
            ingested_count = 0
            
            for raw in raw_jobs:
                # 4. Normalize
                clean_data = self.normalizer.normalize(raw)
                
                # 5. Deduplicate
                job_hash = self.deduplicator.generate_hash(clean_data)
                
                # Check DB for hash
                existing = await self.session.execute(
                    select(Job).where(Job.job_hash == job_hash)
                )
                if existing.scalars().first():
                    dedup_count += 1
                    continue
                
                # 6. Save
                clean_data["job_hash"] = job_hash
                clean_data["source"] = source.name # Override with official source name
                clean_data["source_id"] = source.id
                
                # Remove extra fields not in DB model if any?
                # Using **clean_data directly requires matching fields.
                # Use explicit constructor for safety or filter keys.
                # Assuming Normalizer returns valid keys for JobBase + extras
                
                # Filter keys just in case
                valid_keys = Job.__fields__.keys()
                db_data = {k: v for k, v in clean_data.items() if k in valid_keys}
                
                new_job = Job(**db_data)
                self.session.add(new_job)
                ingested_count += 1
                
            # Update Source Last Run
            source.last_run = datetime.utcnow()
            self.session.add(source)
            
            await self.session.commit()
            
            # 7. Log Success
            duration = time.time() - start_time
            await self._log_result(
                source, "success", 
                found=len(raw_jobs), 
                ingested=ingested_count, 
                dedup=dedup_count,
                duration=duration
            )
            
        except Exception as e:
            await self.session.rollback()
            duration = time.time() - start_time
            await self._log_result(source, "failed", error=str(e), duration=duration)
            raise e

    def _get_strategy(self, source: JobSource) -> JobSourceBase:
        if source.type == "api":
            return APIJobSource(source.config)
        elif source.type == "scraper":
            return PlaywrightScraper(source.config)
        else:
            raise ValueError(f"Unknown source type: {source.type}")

    async def _log_result(self, source: JobSource, status: str, found=0, ingested=0, dedup=0, error=None, duration=0.0):
        log = IngestionLog(
            source_id=source.id,
            status=status,
            jobs_found=found,
            jobs_ingested=ingested,
            jobs_deduplicated=dedup,
            error_message=error,
            duration_seconds=duration
        )
        self.session.add(log)
        await self.session.commit()
