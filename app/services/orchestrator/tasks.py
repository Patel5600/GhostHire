import asyncio
from typing import Dict
from celery import shared_task
from app.core.celery_app import celery_app
from app.db.session import engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

# We need a way to run async code from Celery (sync)
def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@celery_app.task(bind=True, name="task_scrape_job")
def task_scrape_job(self, url: str) -> Dict:
    """
    Wrapper for scraping logic.
    """
    from app.services.scraper.crawlers import GreenhouseScraper
    # NOTE: This is a robust simplification. In real app, we need proper dependency injection for DB logs.
    
    async def _do_scrape():
        scraper = GreenhouseScraper(url, "Unknown")
        return await scraper.scrape()

    results = run_async(_do_scrape())
    return {"jobs_found": len(results), "snippet": results[:1] if results else []}

@celery_app.task(bind=True, name="task_optimize_resume")
def task_optimize_resume(self, resume_text: str, job_text: str) -> Dict:
    from app.services.ai.service import ai_manager
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def _do_optimize():
        async with async_session() as db:
            # Mocking user_id 1 for automated system tasks if not passed
            return await ai_manager.optimize_resume(db, 1, resume_text, job_text)

    return run_async(_do_optimize())

@celery_app.task(bind=True, name="task_apply_job")
def task_apply_job(self, job_url: str, user_id: int) -> bool:
    # This would invoke the automation logic
    return True # Placeholder for the complex browser interaction which might fail in Celery worker if no browser installed
