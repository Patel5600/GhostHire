import io
from pypdf import PdfReader
from fastapi import UploadFile

async def parse_pdf_content(file: UploadFile) -> str:
    """
    Parses text content from a PDF file.
    """
    try:
        # Read file content into memory
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # Parse PDF
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Reset file cursor for further use if needed
        await file.seek(0) 
        
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""
