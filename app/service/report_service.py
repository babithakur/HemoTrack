import os
from werkzeug.utils import secure_filename
from app.utils.blur_utils import check_blur_with_histogram

UPLOAD_FOLDER = "app/static/uploads"
HISTOGRAM_FOLDER = "app/static/histograms"

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
