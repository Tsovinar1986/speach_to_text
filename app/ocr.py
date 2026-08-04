import io
import os

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# Armenian + English + Russian by default; override via env if the source PDFs differ.
OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "hye+eng+rus")
MIN_TEXT_LEN_PER_PAGE = 20


def extract_pdf_text(path: str) -> str:
    """Extract text from a PDF, falling back to OCR on pages with no embedded text (scanned pages)."""
    pages_text = []
    doc = fitz.open(path)
    try:
        for page in doc:
            text = page.get_text().strip()
            if len(text) < MIN_TEXT_LEN_PER_PAGE:
                pix = page.get_pixmap(dpi=300)
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(image, lang=OCR_LANGUAGES).strip()
            if text:
                pages_text.append(text)
    finally:
        doc.close()
    return "\n\n".join(pages_text)
