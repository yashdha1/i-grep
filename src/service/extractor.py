import os
import pytesseract
from PIL import Image
import fitz

# For faster OCR, use tessdata_fast and TESSDATA_PREFIX  
# OCR_CONFIG = "--psm 6 -c tessedit_do_invert=0"
OCR_CONFIG = r'--oem 1 --psm 6'
os.environ["TESSDATA_PREFIX"] = "/home/user/tesseract/tessdata_fast"
MAX_IMAGE_DIM = 2000
os.environ["OMP_THREAD_LIMIT"] = "1"


def extract_text_from_image(image_path):
    """slower but more accurate"""
    try:
        image = Image.open(image_path).convert("L")
        w, h = image.size
        if max(w, h) > MAX_IMAGE_DIM:
            ratio = MAX_IMAGE_DIM / max(w, h)
            image = image.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        text = pytesseract.image_to_string(image, lang="eng", config=OCR_CONFIG)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None

def extract_text_from_pdf(pdf_path): 
    """faster"""
    try:
        pdf = fitz.open(pdf_path)
        text = ""
        for page in pdf:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
