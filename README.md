# HemoTrack 🩸

**HemoTrack** is a web-based medical report management and health-analysis system built with **Python Flask and PostgreSQL**. It combines OCR, computer vision, machine learning, and NLP to help users organize medical reports and obtain meaningful insights from their health data.

> ⚠️ **Medical Disclaimer:** HemoTrack is an academic/software project for educational and informational purposes. Its predictions and recommendations are not medical diagnoses and should not replace professional medical advice.

## ✨ Features

- 📄 **Medical Report Management** — Upload, store, organize, and access medical reports.
- 🔍 **OCR Processing** — Extracts information such as hemoglobin levels and report dates from hematology reports using PyTesseract/Tesseract OCR.
- 🖼️ **Image Quality Validation** — Uses OpenCV's Laplacian variance method to detect blurry or low-quality report images.
- 📊 **Hemoglobin Analysis** — Stores historical hemoglobin values and uses Linear Regression to analyze trends and estimate future levels.
- 👁️ **Conjunctival Analysis** — Processes eye images to analyze redness, saturation, and brightness and generates an explainable anemia-related risk score.
- 🧠 **Symptom Analysis** — Uses Sentence Transformers to analyze symptoms described in natural language and identify potential nutrient deficiencies.
- 🥗 **Dietary Recommendations** — Provides food recommendations based on predicted nutrient deficiencies.

## 🏗️ Architecture

HemoTrack follows a **Route–Service–Repository architecture**:

```text
Routes
   ↓
Services
   ↓
Repositories
```
## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Python, Flask |
| **Database** | PostgreSQL |
| **Machine Learning** | scikit-learn |
| **NLP** | Sentence Transformers |
| **Data Processing** | Pandas, NumPy |
| **Computer Vision** | OpenCV (cv2) |
| **OCR** | PyTesseract, Tesseract OCR |
| **Architecture** | Route–Service–Repository |

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/babithakur/HemoTrack
cd HemoTrack
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```
### 3. Run the Application

```bash
python run.py
```
## 📜 License

**Copyright © 2026 Babi Thakur. All Rights Reserved.**

This project is publicly available on GitHub for **portfolio, educational, demonstration, and recruitment purposes**.

The source code and original materials of **HemoTrack** are proprietary and are **not open source**.

Permission is **not granted** to:

- Copy or reuse the source code in other projects.
- Modify or create derivative works based on the source code.
- Redistribute or republish the source code.
- Use the source code for commercial purposes.
- Present or distribute the project as your own work.

Viewing or downloading this repository does **not** grant permission to use, modify, distribute, or commercially exploit the source code.

For permission to use any part of the HemoTrack source code, please contact the copyright holder.

### Third-Party Dependencies

HemoTrack uses third-party libraries and frameworks, including Flask, PostgreSQL-related libraries, Sentence Transformers, scikit-learn, Pandas, NumPy, PyTesseract, OpenCV, and their dependencies.

These third-party components are **not covered by this proprietary notice** and remain subject to their respective licenses and terms.

---

**Copyright © 2026 Babi Thakur. All Rights Reserved.**

