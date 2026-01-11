from typing import Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from playwright.async_api import Page

from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.resume import Resume
from .browser import BrowserManager
from .forms import FormDetector
from .autofill import ResumeAutofill
from .submitter import FormSubmitter
from .tracker import AutomationTracker

class AutoApplyEngine:
    def __init__(self, session: AsyncSession, application_id: int):
        self.session = session
        self.app_id = application_id
        self.browser_manager = None
        self.context = None
        self.page = None
        self.tracker = AutomationTracker(session, application_id)

    async def run(self):
        try:
            # 1. Init Data
            app = await self.session.get(Application, self.app_id)
            if not app:
                raise ValueError("Application not found")
            
            job = await self.session.get(Job, app.job_id)
            resume = await self.session.get(Resume, app.resume_id) # Assuming resume_id exists
            
            if not job or not resume:
                await self.tracker.log_step("init", "error", "Job or Resume missing")
                return
            
            await self.tracker.update_status(ApplicationStatus.APPLYING)
            await self.tracker.log_step("init", "success", "Starting automation")

            # 2. Prepare Resume Data (Mocking extraction result usage)
            resume_data = resume.parsed_data or {}
            # Flatten or adapt data if needed
            resume_data['email'] = "user@example.com" # Placeholder if not in parsed
            
            # 3. Launch Browser
            self.browser_manager = await BrowserManager.get_instance()
            self.context = await self.browser_manager.create_context()
            self.page = await self.context.new_page()

            # 4. Navigate
            await self.page.goto(job.url)
            await self.tracker.log_step("navigation", "success", f"Visited {job.url}")

            # 5. Initialize Components
            detector = FormDetector()
            autofill = ResumeAutofill(resume_data)
            submitter = FormSubmitter(self.page, detector, autofill)

            # 6. Fill & Submit Loop (Support generic multi-page)
            # Simple single page for now
            await submitter.fill_current_page()
            
            if resume.file_path:
                await submitter.handle_file_upload(resume.file_path)
            
            await self.tracker.log_step("fill_form", "success", "Form filled")

            # 7. Submit
            success = await submitter.submit()
            if success:
                await self.tracker.log_step("submission", "success", "Clicked Submit")
                await self.tracker.update_status(ApplicationStatus.APPLIED)
            else:
                await self.tracker.log_step("submission", "failed", "Could not find submit button")
                await self.tracker.update_status(ApplicationStatus.FAILED)

        except Exception as e:
            await self.tracker.log_step("error", "failed", str(e))
            await self.tracker.update_status(ApplicationStatus.FAILED)
            if self.page:
                try:
                    path = f"error_{self.app_id}.png"
                    await self.page.screenshot(path=path)
                    await self.tracker.log_step("screenshot", "info", screenshot=path)
                except:
                    pass
            raise e
        finally:
            if self.context:
                await self.context.close()
            # Browser manager instance is shared, usually don't close browser here
