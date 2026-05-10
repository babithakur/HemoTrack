import cv2
import numpy as np

eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

def detect_and_crop_eyes(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    if len(eyes) == 0:
        return []
    eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
    eye_crops = []
    for (x, y, w, h) in eyes:
        pad_x, pad_y = int(w * 0.15), int(h * 0.25)
        x1, y1 = max(0, x - pad_x), max(0, y - pad_y)
        x2, y2 = min(image.shape[1], x + w + pad_x), min(image.shape[0], y + h + pad_y)
        eye_crop = image[y1:y2, x1:x2]
        eye_crops.append({"bbox": (x1, y1, x2, y2), "eye": eye_crop})
    return sorted(eye_crops, key=lambda e: e["bbox"][0])


def extract_conjunctiva_from_eye(eye_img):
    h, w = eye_img.shape[:2]
    x1, x2 = int(w * 0.30), int(w * 0.70)
    y1, y2 = int(h * 0.60), int(h * 0.90)
    roi = eye_img[y1:y2, x1:x2]
    roi = roi[int(roi.shape[0] * 0.30):, :]
    return roi

def preprocess_roi(roi):
    roi = cv2.resize(roi, (200, 100))
    roi = cv2.GaussianBlur(roi, (5, 5), 0)
    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
    if np.mean(l) < 120:
        l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    roi = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return roi

def extract_anemia_features(roi):
    if roi.size == 0:
        return None
    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    H, S, V = cv2.split(hsv)
    mask = V > 50
    if np.sum(mask) == 0:
        return None
    return {
        "mean_lightness": float(np.mean(L[mask])),
        "mean_redness": float(np.mean(A[mask])),
        "mean_saturation": float(np.mean(S[mask])),
        "mean_value": float(np.mean(V[mask]))
    }

def average_features(feature_list):
    if not feature_list:
        return None
    return {k: round(np.mean([f[k] for f in feature_list]), 2) for k in feature_list[0].keys()}

# def predict_anemia(features):
#     redness, saturation, lightness = features["mean_redness"], features["mean_saturation"], features["mean_lightness"]
#     score = 0

#     if saturation < 30: score += 50   # was <20
#     elif saturation < 45: score += 30 # was <35

#     if redness < 145: score += 30     # was <132
#     if lightness > 115: score += 20   # was >120

#     if score >= 70: return "High anemia likelihood", score
#     elif score >= 40: return "Moderate anemia likelihood", score
#     else: return "Low anemia likelihood", score

def predict_anemia(features):
    redness, saturation, lightness = (
        features["mean_redness"],
        features["mean_saturation"],
        features["mean_lightness"]
    )
    score = 0
    contributions = {}

    # Saturation contribution
    if saturation < 30:
        contributions["saturation"] = +50
        score += 50
    elif saturation < 45:
        contributions["saturation"] = +30
        score += 30
    else:
        contributions["saturation"] = 0

    # Redness contribution
    if redness < 145:
        contributions["redness"] = +30
        score += 30
    else:
        contributions["redness"] = 0

    # Lightness contribution
    if lightness > 115:
        contributions["lightness"] = +20
        score += 20
    else:
        contributions["lightness"] = 0

    # Final prediction
    if score >= 70:
        prediction = "High anemia likelihood"
    elif score >= 40:
        prediction = "Moderate anemia likelihood"
    else:
        prediction = "Low anemia likelihood"

    return {
        "prediction": prediction,
        "score": score,
        "contributions": contributions
    }

