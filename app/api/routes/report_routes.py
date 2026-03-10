from flask import Blueprint, render_template, request, flash
from app.service.report_service import ReportService

report_bp = Blueprint("report", __name__)

@report_bp.route("/validate")
def validate():
    return render_template("validate.html")

@report_bp.route("/blur_analysis", methods=["POST"])
def blur_analysis():
    file = request.files.get("file")
    filename = request.form.get("filename")

    if not file or not filename:
        flash("File and filename are required", "error")
        return render_template("dashboard.html")
    try:
        result = ReportService.analyze_blur(file, filename)
        # Pass results to template for display
        return render_template("blur_analysis.html", result=result)
    except Exception as e:
        flash(str(e), "error")
        return render_template("dashboard.html")