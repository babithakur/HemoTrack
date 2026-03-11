import os
from werkzeug.utils import secure_filename
from app.utils.blur_utils import check_blur_with_histogram
from app.utils.ocr_utils import run_ocr
from datetime import datetime
from sentence_transformers import SentenceTransformer
from app.repo.report_repo import ReportRepo
from app.utils.report_utils import categorize_report


UPLOAD_FOLDER = "app/static/uploads"
HISTOGRAM_FOLDER = "app/static/histograms"
PREPROCESSED_FOLDER = "app/static/preprocessed"
#embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

class ReportService:
    @staticmethod
    def analyze_blur(file, filename, threshold=100.0):
        #ensure folders exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(HISTOGRAM_FOLDER, exist_ok=True)

        #save uploaded file temporarily
        safe_filename = secure_filename(filename) + os.path.splitext(file.filename)[1]
        image_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        file.save(image_path)

        #histogram image path
        histogram_filename = safe_filename.replace(".", "_hist.")
        histogram_path = os.path.join(HISTOGRAM_FOLDER, histogram_filename)

        #run blur analysis
        variance, threshold, image_filename, histogram_image_filename = check_blur_with_histogram(
            image_path, histogram_path, threshold
        )

        return {
            "variance_value": round(variance, 2),
            "threshold": threshold,
            "image_filename": image_filename,
            "histogram_image_filename": histogram_image_filename
        }
    
    @staticmethod
    def validate_report(filename):
        """
        Reuse the already uploaded image from blur analysis.
        Only generate preprocessed image and run OCR.
        """
        os.makedirs(PREPROCESSED_FOLDER, exist_ok=True)

        #path to the already uploaded image
        image_path = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(image_path):
            raise FileNotFoundError("Uploaded image not found. Please run blur analysis first.")

        #preprocessed image path
        preprocessed_filename = filename.replace(".", "_pre.")
        preprocessed_path = os.path.join(PREPROCESSED_FOLDER, preprocessed_filename)

        #run OCR
        hb_value, report_date, image_filename, preprocessed_filename = run_ocr(image_path, preprocessed_path)

        return {
            "hb_value": hb_value,
            "report_date": report_date,
            "original_image": image_filename,
            "preprocessed_image": preprocessed_filename
        }
    
    @staticmethod
    def save_report(user_id, filename, hemoglobin, doctor_note, report_date, image_path):
        # normalize date
        if isinstance(report_date, str):
            report_date = datetime.strptime(report_date, "%Y-%m-%d").date()

        # categorize report using OCR keywords
        category, matched_keywords = categorize_report(image_path)

        # save report
        report = ReportRepo.save_report(
            user_id=user_id,
            category=category,
            filename=filename,
            hemoglobin=hemoglobin,
            doctor_note=doctor_note,
            report_date=report_date
        )

        # generate embedding from OCR text
        text_repr = f"Hb: {hemoglobin}, Date: {report_date}, Category: {category}, Keywords: {matched_keywords}"
        vector = embedding_model.encode(text_repr).tolist()

        ReportRepo.save_embedding(report.report_id, user_id, vector)

        return report
