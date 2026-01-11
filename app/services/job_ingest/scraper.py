from typing import List, Dict, Any
from playwright.async_api import async_playwright
from .base import JobSourceBase

class PlaywrightScraper(JobSourceBase):
    """
    Headless browser scraper using Playwright.
    """
    
    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        url = self.config.get("url")
        # Selector config
        container_selector = self.config.get("container_selector") 
        title_selector = self.config.get("title_selector")
        company_selector = self.config.get("company_selector")
        
        jobs = []
        
        async with async_playwright() as p:
            # Launch browser (could be configured to connect to remote ws)
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle")
                
                # Optional: Handle infinite scroll or pagination logic here
                
                # Get elements
                elements = await page.query_selector_all(container_selector)
                
                for el in elements:
                    title_el = await el.query_selector(title_selector)
                    company_el = await el.query_selector(company_selector)
                    link_el = await el.query_selector("a") # assume link is anchor tag inside
                    
                    if title_el:
                        title = await title_el.inner_text()
                        company = await company_el.inner_text() if company_el else "Unknown"
                        href = await link_el.get_attribute("href") if link_el else ""
                        
                        # Handle relative URLs
                        if href and not href.startswith("http"):
                           href = url + href # Simplification
                        
                        jobs.append({
                            "title": title,
                            "company": company,
                            "url": href,
                            "location": "Unknown", # Would need selector
                            "description": "", # Usually need to visit detail page
                            "source": "scraper_playwright"
                        })
                        
            except Exception as e:
                print(f"Scraping error: {e}")
                # Log error
            finally:
                await browser.close()
                
        return jobs

    async def validate_config(self) -> bool:
        required = ["url", "container_selector", "title_selector"]
        return all(k in self.config for k in required)
