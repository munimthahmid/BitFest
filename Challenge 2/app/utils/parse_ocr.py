"""
parse_ocr.py
Utility for extracting text from images via Tesseract OCR.
"""
import pytesseract
from PIL import Image

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from the image at image_path using pytesseract.
    Returns the raw text as a string.
    """
    # Open the image using PIL
    img = Image.open(image_path)
    # Perform OCR using pytesseract
    extracted_text = pytesseract.image_to_string(img)
    return extracted_text
