from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional

class BrowserManager:
    _instance = None
    _browser: Optional[Browser] = None
    _playwright = None

    @classmethod
    async def get_instance(cls):
        if not cls._instance:
            cls._instance = BrowserManager()
        return cls._instance

    async def get_browser(self) -> Browser:
        if not self._browser:
            self._playwright = await async_playwright().start()
            # In production, you might want to perform browser context management more carefully
            # or connect to a remote browser (ws://...)
            self._browser = await self._playwright.chromium.launch(
                headless=False, # True for prod, False for debugging
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
        return self._browser

    async def create_context(self) -> BrowserContext:
        browser = await self.get_browser()
        # Create a context with specific user agent or viewport
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        return context

    async def close(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
