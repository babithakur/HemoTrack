import os
import secrets 
from werkzeug.utils import secure_filename
from app.utils.blur_utils import check_blur_with_histogram
from app.utils.ocr_utils import run_ocr
from datetime import datetime
from sentence_transformers import SentenceTransformer
from app.repo.report_repo import ReportRepo
from app.utils.report_utils import categorize_report
from flask import session, current_app
from PIL import Image,  ImageOps


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
        category, matched_keywords = categorize_report(image_path)

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
            "histogram_image_filename": histogram_image_filename,
            "category": category
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
    def save_report(hemoglobin, doctor_note, report_date):
        random_hex = secrets.token_hex(6 // 2)
        if report_date:
            # normalize date
            if isinstance(report_date, str):
                report_date = datetime.strptime(report_date, "%Y-%m-%d").date()
        
            # Parse the date string to extract month abbreviation and year
            month_abbr = report_date.strftime("%b")  # e.g., "Feb"
            year = report_date.strftime("%Y")        # e.g., "2026"
            new_filename_base = f"Report_{month_abbr}_{year}_{random_hex}"
            category = "hematology"
        else:
            new_filename_base = f"Report_{random_hex}"
            category = "others"
        
        new_filename = None

        # Find temp image
        for file in os.listdir(UPLOAD_FOLDER):
            if "temp_file" in file:
                old_path = os.path.join(UPLOAD_FOLDER, file)
                # PDF filename
                new_filename = new_filename_base + ".pdf"
                new_path = os.path.join(UPLOAD_FOLDER, new_filename)
                # Convert image to PDF
                image = Image.open(old_path)
                # Fix rotation
                image = ImageOps.exif_transpose(image)
                # Convert to RGB (important for PNG/JPG compatibility)
                if image.mode != "RGB":
                    image = image.convert("RGB")
                image.save(new_path, "PDF", resolution=100.0)
                # Remove original image
                os.remove(old_path)
                break

        if not new_filename:
            raise ValueError("Temp file not found")

        # Rename temp file
        # for file in os.listdir(UPLOAD_FOLDER):
        #     if "temp_file" in file:
        #         old_path = os.path.join(UPLOAD_FOLDER, file)
        #         ext = os.path.splitext(file)[1]  # preserve original extension
        #         new_filename = new_filename_base + ext
        #         new_path = os.path.join(UPLOAD_FOLDER, new_filename)
        #         os.rename(old_path, new_path)
        #         break

        # categorize report using OCR keywords
        #image_path = os.path.join(UPLOAD_FOLDER, new_filename)
        #category, matched_keywords = categorize_report(image_path)

        # save report
        report = ReportRepo.save_report(
            user_id=session["user_id"],
            category=category,
            filename=new_filename,
            hemoglobin=hemoglobin,
            doctor_note=doctor_note,
            report_date=report_date
        )

        # generate embedding from OCR text
        #text_repr = f"Hb: {hemoglobin}, Date: {report_date}, Category: {category}, Keywords: {matched_keywords}"
        # convert to list of Python floats (float64)
        #vector = [float(x) for x in embedding_model.encode(text_repr).tolist()]

        #ReportRepo.save_embedding(report.report_id, session["user_id"], vector)

        return report
    
    @staticmethod
    def get_user_reports():
        user_id = session.get("user_id")

        if not user_id:
            return [], []

        reports = ReportRepo.get_reports_by_user(user_id)

        hematology_reports = []
        other_reports = []

        for report in reports:
            if report.category == "hematology":
                hematology_reports.append(report)
            else:
                other_reports.append(report)

        return hematology_reports, other_reports
    
    @staticmethod
    def delete_report(report_id):
        report = ReportRepo.get_report_by_id(report_id)
        user_id = session.get("user_id")
        if not report or report.user_id != user_id:
            return False

        # Delete file from uploads folder
        file_path = os.path.join(UPLOAD_FOLDER, report.filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete from database
        ReportRepo.delete_report(report)
        return True
