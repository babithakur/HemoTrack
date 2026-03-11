import cv2
import pytesseract
import re
import os
from datetime import datetime

def preprocess_modes(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    mode1 = gray
    mode2 = cv2.adaptiveThreshold(gray, 255,
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, 35, 11)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    mode3 = clahe.apply(gray)

    return [("grayscale", mode1), ("adaptive", mode2), ("clahe", mode3)]


def extract_data(img):
    df = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME)
    df = df.dropna().reset_index(drop=True)
    return df

def extract_hemoglobin(df):
    for i, row in df.iterrows():
        text = str(row['text']).lower()
        if any(k in text for k in ["haemoglobin", "hemoglobin", "hb", "hb:"]):
            for j in range(i+1, min(i+6, len(df))):
                token = str(df.loc[j, "text"])
                match = re.search(r"\d+\.?\d*", token)
                if match:
                    val = float(match.group())
                    if val > 20:
                        val = val / 10
                    return str(val)
    return None

def extract_date(df):
    text_all = " ".join(df["text"].astype(str).tolist())
    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b"
    ]
    for pat in patterns:
        match = re.search(pat, text_all, re.IGNORECASE)
        if match:
            return match.group()
    return None

from datetime import datetime

def normalize_date(date_str):
    if not date_str:
        return None

    # Common formats to try
    formats = [
        "%b %d, %Y",   # Jun 22, 2023
        "%B %d, %Y",   # June 22, 2023
        "%d/%m/%Y",    # 22/06/2023
        "%d-%m-%Y",    # 22-06-2023
        "%Y-%m-%d",    # 2023-06-22
        "%Y/%m/%d",    # 2024/06/23
        "%d.%m.%Y",    # 22.06.2023
        "%d/%m/%y",    # 22/06/23 (short year)
        "%Y.%m.%d"     # 2024.06.23
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")  # ISO format for HTML <input type="date">
        except ValueError:
            continue

    return None

def run_ocr(image_path, preprocessed_path):
    modes = preprocess_modes(image_path)

    hb_value = None
    report_date = None
    chosen_mode_name = None
    chosen_img = None

    for name, img in modes:
        df = extract_data(img)
        hb_value = extract_hemoglobin(df)
        report_date_raw = extract_date(df)
        report_date = normalize_date(report_date_raw) if report_date_raw else None

        if hb_value:
            chosen_mode_name = name
            chosen_img = img
            break

    if chosen_img is not None:
        cv2.imwrite(preprocessed_path, chosen_img)

    return hb_value, report_date, os.path.basename(image_path), os.path.basename(preprocessed_path)
