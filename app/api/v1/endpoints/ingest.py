from typing import List, Any
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api import deps
from app.services.scraper.crawlers import GreenhouseScraper, LeverScraper
from app.services.ingest_service import IngestService
from app.services.scraper.browser import browser_manager

router = APIRouter()

async def run_scrape_job(url: str, type: str, session_factory):
    """
    Background task to run scraping.
    We need a fresh session for the background task.
    """
    # Note: In a real app complexity, session management for bg tasks needs care.
    # Here we instantiate a session manually.
    async with session_factory() as session:
        scraper = None
        if type == "greenhouse":
            scraper = GreenhouseScraper(url, company_name="Unknown") # Ideally we scrape company name or pass it
        elif type == "lever":
            scraper = LeverScraper(url, company_name="Unknown")
        
        if scraper:
            jobs = await scraper.scrape()
            ingest = IngestService(session)
            await ingest.ingest_jobs(jobs, url)

@router.post("/trigger")
async def trigger_ingest(
    url: str,
    type: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_session)
) -> Any:
    """
    Trigger a scrape job for a specific URL.
    Type: 'greenhouse' or 'lever'
    """
    if type not in ["greenhouse", "lever"]:
        raise HTTPException(400, "Invalid scraper type")
        
    # We can't pass the 'db' session to background task easily as it might close.
    # We rely on a pattern where we might need to create a new session in the task.
    # For simplicity, we will run it inline or use a hack. 
    # BETTER: Just run inline for this demo if it's fast, or use proper worker.
    # Given 'async', we can just await it if we accept the latency, OR use a global session factory.
    
    # For this deliverable, let's just await it to ensure it works and return result immediately, 
    # or finding a way to get session factory. 
    # 'deps.get_session' is a generator.
    
    # Re-using the logic from db/session.py
    from app.db.session import engine
    from sqlalchemy.orm import sessionmaker
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    background_tasks.add_task(run_scrape_job, url, type, async_session)
    
    return {"message": "Scrape job triggered in background"}
