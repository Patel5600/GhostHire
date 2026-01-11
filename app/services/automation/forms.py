from playwright.async_api import Page, ElementHandle
from typing import List, Dict, Any, Optional

class FormDetector:
    """
    Heuristics to detect form fields on a page.
    """
    
    async def detect_fields(self, page: Page) -> List[Dict[str, Any]]:
        """
        Scans the page for input, select, and textarea elements.
        Returns a list of field metadata.
        """
        fields = []
        
        # Get all inputs
        inputs = await page.query_selector_all("input:not([type='hidden']), textarea, select")
        
        for el in inputs:
            meta = await self._get_field_metadata(el)
            if meta:
                fields.append(meta)
                
        return fields

    async def _get_field_metadata(self, el: ElementHandle) -> Optional[Dict[str, Any]]:
        try:
            tag_name = await el.evaluate("(e) => e.tagName.toLowerCase()")
            input_type = await el.get_attribute("type") or "text"
            name_attr = await el.get_attribute("name") or ""
            id_attr = await el.get_attribute("id") or ""
            
            # Label heuristic
            label_text = ""
            if id_attr:
                # Try explicit label
                label_handle = await el.page.query_selector(f"label[for='{id_attr}']")
                if label_handle:
                    label_text = await label_handle.inner_text()
            
            if not label_text and name_attr:
                 label_text = name_attr # Fallback
                 
            # Aria label
            if not label_text:
                label_text = await el.get_attribute("aria-label") or ""

            return {
                "element": el,
                "tag": tag_name,
                "type": input_type,
                "name": name_attr,
                "id": id_attr,
                "label": label_text.strip().lower()
            }
        except Exception:
            return None
