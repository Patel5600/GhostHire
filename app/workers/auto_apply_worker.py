import asyncio
from celery.utils.log import get_task_logger
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import engine
from app.services.automation.engine import AutoApplyEngine
from app.core.celery_app import celery_app

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=2, default_retry_delay=30, name="app.workers.auto_apply_worker.run_auto_apply")
def run_auto_apply(self, application_id: int):
    """
    Celery task to run auto-apply automation.
    """
    logger.info(f"Starting auto-apply for application_id: {application_id}")

    async def _run():
        async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session_factory() as session:
            automation_engine = AutoApplyEngine(session, application_id)
            await automation_engine.run()

    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(_run())
        logger.info(f"Auto-apply finished for application_id: {application_id}")

    except Exception as exc:
        logger.error(f"Auto-apply failed for {application_id}: {exc}")
        raise self.retry(exc=exc)
