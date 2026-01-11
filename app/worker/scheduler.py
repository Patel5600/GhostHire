from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from app.workers.job_ingest_worker import run_ingestion_task # Future integration

scheduler = AsyncIOScheduler()

def start_scheduler():
    # Example daily job logic would go here.
    # Currently, ingestion is triggered via API or Celery Beats (if configured).
    
    # if not scheduler.running:
    #     scheduler.start()
    #     print("Scheduler started...")
    pass

async def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
