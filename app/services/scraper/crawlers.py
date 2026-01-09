import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict
from bs4 import BeautifulSoup
from app.services.scraper.browser import browser_manager

class BaseScraper(ABC):
    def __init__(self, base_url: str, company_name: str):
        self.base_url = base_url
        self.company_name = company_name

    def generate_id(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    @abstractmethod
    async def scrape(self) -> List[Dict]:
        pass

class GreenhouseScraper(BaseScraper):
    async def scrape(self) -> List[Dict]:
        page, context = await browser_manager.get_page()
        jobs = []
        try:
            # Greenhouse often embeds in id="grnhse_app" or just lists
            # A common pattern: https://boards.greenhouse.io/{company}
            await page.goto(self.base_url, wait_until="networkidle")
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Generic Greenhouse selector (may vary slightly)
            job_posts = soup.find_all('div', class_='opening') 
            if not job_posts:
                 job_posts = soup.find_all('section', class_='level-0')

            for post in job_posts:
                link = post.find('a')
                if link:
                    title = link.get_text(strip=True)
                    url = link.get('href')
                    if not url.startswith('http'):
                        url = f"https://boards.greenhouse.io{url}"
                    
                    location_div = post.find('span', class_='location')
                    location = location_div.get_text(strip=True) if location_div else "Remote"
                    
                    jobs.append({
                        "title": title,
                        "company": self.company_name,
                        "url": url,
                        "location": location,
                        "job_hash": self.generate_id(url),
                        "source": "Greenhouse"
                    })
        except Exception as e:
            print(f"Error scraping {self.base_url}: {e}")
        finally:
            await context.close()
        return jobs

class LeverScraper(BaseScraper):
    async def scrape(self) -> List[Dict]:
        page, context = await browser_manager.get_page()
        jobs = []
        try:
            # Lever pattern: https://jobs.lever.co/{company}
            await page.goto(self.base_url, wait_until="networkidle")
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            job_posts = soup.find_all('a', class_='posting-title')
            
            for post in job_posts:
                title_h5 = post.find('h5')
                title = title_h5.get_text(strip=True) if title_h5 else "Unknown"
                url = post.get('href')
                
                # Location often in a span
                meta = post.find('span', class_='sort-by-location')
                location = meta.get_text(strip=True) if meta else "Remote"

                jobs.append({
                    "title": title,
                    "company": self.company_name,
                    "url": url,
                    "location": location,
                    "job_hash": self.generate_id(url),
                    "source": "Lever"
                })
        except Exception as e:
            print(f"Error scraping {self.base_url}: {e}")
        finally:
            await context.close()
        return jobs

class GenericScraper(BaseScraper):
    """
    Experimental generic scraper for simple career pages.
    """
    async def scrape(self) -> List[Dict]:
        page, context = await browser_manager.get_page()
        jobs = []
        try:
            await page.goto(self.base_url, wait_until="networkidle")
            # Heuristic: Find all links that contain "apply" or "job" or "career"
            links = await page.query_selector_all("a")
            
            for link in links:
                text = await link.inner_text()
                href = await link.get_attribute("href")
                
                if href and ("apply" in href.lower() or "job" in href.lower() or "career" in href.lower()):
                     if not href.startswith("http"):
                         # simplistic join
                         href = self.base_url + href
                     
                     jobs.append({
                        "title": text[:100] if text else "Unknown Job",
                        "company": self.company_name,
                        "url": href,
                        "location": "Unknown",
                        "job_hash": self.generate_id(href),
                        "source": "Generic"
                    })
        except Exception as e:
            print(f"Error scraping {self.base_url}: {e}")
        finally:
            await context.close()
        return jobs
