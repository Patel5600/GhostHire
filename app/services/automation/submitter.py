from playwright.async_api import Page
from typing import Dict, Any, List
from .forms import FormDetector
from .autofill import ResumeAutofill

class FormSubmitter:
    """
    Executes the filling and submission of forms.
    """
    
    def __init__(self, page: Page, detector: FormDetector, autofill: ResumeAutofill):
        self.page = page
        self.detector = detector
        self.autofill = autofill

    async def fill_current_page(self):
        # 1. Detect Fields
        fields = await self.detector.detect_fields(self.page)
        
        # 2. Iterate and Fill
        for field in fields:
            value = self.autofill.map_field(field)
            if value:
                element = field["element"]
                tag = field["tag"]
                f_type = field["type"]
                
                try:
                    if tag == "input" and f_type in ["text", "email", "tel", "url"]:
                        await element.fill(value)
                    elif tag == "textarea":
                        await element.fill(value)
                    elif tag == "select":
                        # Attempt to select by value or label (simplified)
                        await element.select_option(value=value)
                except Exception as e:
                    print(f"Failed to fill {field['name']}: {e}")

    async def handle_file_upload(self, file_path: str):
        # Look for file input
        file_input = await self.page.query_selector("input[type='file']")
        if file_input:
            await file_input.set_input_files(file_path)

    async def submit(self):
        # Heuristic for submit button
        # Look for button with type='submit' or text 'Submit', 'Apply', 'Next'
        submit_btn = await self.page.query_selector("button[type='submit'], input[type='submit']")
        if not submit_btn:
            # Try finding by text
            btns = await self.page.query_selector_all("button, a.btn")
            for btn in btns:
                text = (await btn.inner_text()).lower()
                if "submit" in text or "apply" in text or "next" in text:
                    submit_btn = btn
                    break
        
        if submit_btn:
            await submit_btn.click()
            # Wait for navigation or change
            try:
                await self.page.wait_for_load_state("networkidle", timeout=5000)
            except:
                pass
            return True
        return False
