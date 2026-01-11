from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.application import SubmissionLog, Application, ApplicationStatus
from datetime import datetime

class AutomationTracker:
    def __init__(self, session: AsyncSession, application_id: int):
        self.session = session
        self.app_id = application_id

    async def log_step(self, step: str, status: str, message: str = None, screenshot: str = None):
        log = SubmissionLog(
            application_id=self.app_id,
            step=step,
            status=status,
            message=message,
            screenshot_path=screenshot
        )
        self.session.add(log)
        await self.session.commit()

    async def update_status(self, status: ApplicationStatus):
        app = await self.session.get(Application, self.app_id)
        if app:
            app.status = status
            app.updated_at = datetime.utcnow()
            self.session.add(app)
            await self.session.commit()
