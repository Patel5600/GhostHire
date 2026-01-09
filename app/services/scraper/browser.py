from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Manages the Playwright browser instance.
    """
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            # Launch chromium in headless mode
            # args can be added to reduce detection, e.g. --disable-blink-features=AutomationControlled
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            logger.info("Browser started")

    async def get_page(self):
        if not self.browser:
            await self.start()
        
        context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        return page, context

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser stopped")

browser_manager = BrowserManager()
