from typing import List, Dict
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.job import Job
from app.models.company import Company
from app.models.crawl_log import CrawlLog

class IngestService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def ingest_jobs(self, jobs_data: List[Dict], source_url: str):
        jobs_added = 0
        company_cache = {}

        for job_data in jobs_data:
            # 1. Handle Company
            company_name = job_data.get("company")
            if company_name not in company_cache:
                result = await self.session.execute(select(Company).where(Company.name == company_name))
                company = result.scalars().first()
                if not company:
                    company = Company(name=company_name)
                    self.session.add(company)
                    await self.session.commit()
                    await self.session.refresh(company)
                company_cache[company_name] = company
            
            # 2. Check Deduplication
            job_hash = job_data.get("job_hash")
            existing_job = await self.session.execute(select(Job).where(Job.job_hash == job_hash))
            if existing_job.scalars().first():
                continue

            # 3. Create Job
            new_job = Job(
                title=job_data["title"],
                company=company_name, # keeping legacy string field
                location=job_data.get("location"),
                url=job_data["url"],
                source=job_data.get("source"),
                job_hash=job_hash,
                description=f"Imported from {job_data.get('source')}" 
            )
            self.session.add(new_job)
            jobs_added += 1
        
        # 4. Log Crawl
        log = CrawlLog(
            source=source_url,
            status="success",
            jobs_found=len(jobs_data),
            jobs_ingested=jobs_added
        )
        self.session.add(log)
        await self.session.commit()
        
        return {"found": len(jobs_data), "ingested": jobs_added}
