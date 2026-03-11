# app/utils/report_utils.py
import cv2
import pytesseract

CBC_KEYWORDS = [
    "hemoglobin", "hb", "wbc", "tlc", "total leucocyte",
    "rbc", "red blood cell", "platelet", "plt", "mcv", "mch", "mchc"
]

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found or cannot be opened.")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray

def extract_text(img):
    text = pytesseract.image_to_string(img)
    return text.lower()

def categorize_report(image_path, threshold=3):
    """
    Categorize report as CBC or Other based on keyword matches.
    threshold: minimum number of CBC keywords required to classify as CBC.
    """
    img = preprocess_image(image_path)
    text = extract_text(img)

    matches = [kw for kw in CBC_KEYWORDS if kw in text]
    if len(matches) >= threshold:
        return "hematology", matches
    else:
        return "others", matches
