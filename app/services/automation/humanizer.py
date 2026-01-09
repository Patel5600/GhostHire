import asyncio
import random
from playwright.async_api import Page, ElementHandle

class Humanizer:
    """
    Simulates human-like behavior to avoid bot detection.
    """
    
    @staticmethod
    async def random_delay(min_ms: int = 500, max_ms: int = 2000):
        delay = random.randint(min_ms, max_ms) / 1000.0
        await asyncio.sleep(delay)

    @staticmethod
    async def natural_type(element: ElementHandle, text: str):
        """Types text with variable speed."""
        delay = random.randint(30, 100)
        await element.type(text, delay=delay)
        await Humanizer.random_delay(200, 500)

    @staticmethod
    async def scroll_to_view(page: Page, element: ElementHandle):
        await element.scroll_into_view_if_needed()
        await Humanizer.random_delay(300, 700)
