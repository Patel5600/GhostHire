import abc
import logging
import asyncio
from typing import Dict
from playwright.async_api import Page

from app.services.scraper.browser import browser_manager
from app.services.automation.humanizer import Humanizer
from app.models.user import User

logger = logging.getLogger(__name__)

class BaseApplier(abc.ABC):
    def __init__(self, user: User, resume_path: str):
        self.user = user
        self.resume_path = resume_path

    @abc.abstractmethod
    async def apply(self, url: str) -> bool:
        pass

    async def fill_common_fields(self, page: Page):
        """
        Heuristic field filling.
        """
        # Dictionary of field naming conventions (lowercase)
        mappings = {
            "first_name": ["first name", "firstname", "first"],
            "last_name": ["last name", "lastname", "last"],
            "email": ["email", "e-mail"],
            "phone": ["phone", "mobile", "cell"],
            "linkedin": ["linkedin", "linked in"],
            "portfolio": ["portfolio", "website", "url"],
            "resume": ["resume", "cv", "upload"]
        }
        
        # Naive implementation: Iterate inputs and check labels/placeholders
        inputs = await page.query_selector_all("input")
        for inp in inputs:
            try:
                # Get context: id, name, label
                attr_id = await inp.get_attribute("id") or ""
                attr_name = await inp.get_attribute("name") or ""
                # Try to find associated label
                # In real scenario, use page.get_by_label for better results
                
                context_str = (attr_id + " " + attr_name).lower()
                
                # Check mapping
                if any(k in context_str for k in mappings["first_name"]):
                    name_parts = (self.user.full_name or "").split(" ")
                    await Humanizer.natural_type(inp, name_parts[0])
                elif any(k in context_str for k in mappings["last_name"]):
                    name_parts = (self.user.full_name or "").split(" ")
                    if len(name_parts) > 1:
                        await Humanizer.natural_type(inp, " ".join(name_parts[1:]))
                elif any(k in context_str for k in mappings["email"]):
                    await Humanizer.natural_type(inp, self.user.email)
                # ... Add more fields
                
            except Exception:
                continue

class GreenhouseApplier(BaseApplier):
    async def apply(self, url: str) -> bool:
        page, context = await browser_manager.get_page()
        try:
            logger.info(f"Applying to Greenhouse: {url}")
            await page.goto(url, wait_until="networkidle")
            await Humanizer.random_delay(1000, 3000)

            # Heuristic selectors for Greenhouse
            # Resume Upload
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                # In prod, stream file from S3 to temp path
                # For now using local mock path or mapped volume
                await file_input.set_input_files(self.resume_path)
                logger.info("Uploaded Resume")
            
            # Form Filling
            await self.fill_common_fields(page)
            
            # Submit Button
            submit = await page.query_selector("#submit_app")
            if submit:
                # await submit.click() # DISABLED FOR SAFETY/TESTING
                # await page.wait_for_navigation()
                logger.info("Form filled (Submission mocked)")
                return True
            else:
                logger.warning("Submit button not found")
                return False

        except Exception as e:
            logger.error(f"Greenhouse application failed: {e}")
            return False
        finally:
            await context.close()

class LeverApplier(BaseApplier):
    async def apply(self, url: str) -> bool:
        page, context = await browser_manager.get_page()
        try:
            await page.goto(url, wait_until="networkidle")
            await Humanizer.random_delay()
            
            # Apply button often redirects to form
            apply_btn = await page.query_selector("a.postings-btn")
            if apply_btn:
                await apply_btn.click()
                await Humanizer.random_delay()

            # Upload Resume
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                 await file_input.set_input_files(self.resume_path)

            await self.fill_common_fields(page)
            
            logger.info("Lever Form filled (Submission mocked)")
            return True
        except Exception as e:
            logger.error(f"Lever failed: {e}")
            return False
        finally:
            await context.close()
