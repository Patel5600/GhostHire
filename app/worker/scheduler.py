from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api.v1.endpoints.ingest import run_scrape_job
from app.db.session import engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

scheduler = AsyncIOScheduler()

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def start_scheduler():
    # Example daily job: Scrape known career pages
    # In production, fetch these URLs from the Company database table where 'careers_page_url' is set.
    
    # scheduler.add_job(
    #     run_scrape_job, 
    #     'cron', 
    #     hour=0, 
    #     minute=0, 
    #     args=["https://boards.greenhouse.io/example", "greenhouse", async_session]
    # )
    
    scheduler.start()
    print("Scheduler started...")

async def stop_scheduler():
    scheduler.shutdown()
