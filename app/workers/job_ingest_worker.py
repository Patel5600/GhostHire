import asyncio
from celery.utils.log import get_task_logger
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import engine
from app.services.job_ingest.pipeline import IngestPipeline
from app.core.celery_app import celery_app

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="app.workers.job_ingest_worker.run_ingestion_task")
def run_ingestion_task(self, source_id: int):
    """
    Celery task to run ingestion pipeline.
    Wraps async execution in synchronous Celery worker.
    """
    logger.info(f"Starting ingestion for source_id: {source_id}")
    
    async def _run():
        # Create a new session for this task
        async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session_factory() as session:
            pipeline = IngestPipeline(session)
            await pipeline.run(source_id)

    try:
        # Ensure we have an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(_run())
        logger.info(f"Ingestion finished for source_id: {source_id}")

    except Exception as exc:
        logger.error(f"Ingestion failed for source_id {source_id}: {exc}")
        # Exponential backoff: 60s, 120s, 240s...
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)
