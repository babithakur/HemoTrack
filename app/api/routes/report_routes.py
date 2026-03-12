from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.service.report_service import ReportService

report_bp = Blueprint("report", __name__)

@report_bp.route("/blur_analysis", methods=["POST"])
def blur_analysis():
    file = request.files.get("file")
    #filename = request.form.get("filename")

    # if not file or not filename:
    #     flash("File and filename are required", "error")
    #     return render_template("dashboard.html")
    
    if not file:
        flash("File is required", "error")
        return render_template("dashboard.html")
    try:
        filename = "temp_file"
        result = ReportService.analyze_blur(file, filename)
        # Pass results to template for display
        return render_template("blur_analysis.html", result=result)
    except Exception as e:
        flash(str(e), "error")
        return render_template("dashboard.html")

@report_bp.route("/validate", methods=["GET"])
def validate_report():
    filename = request.args.get("filename")  #reuse filename from blur analysis

    try:
        result = ReportService.validate_report(filename)
        ReportService.validate_report(filename)
        return render_template("validate.html", 
                               extracted_hb=result["hb_value"],
                               extracted_date=result["report_date"],
                               original_image=result["original_image"],
                               preprocessed_image=result["preprocessed_image"])
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(str(e), "error")
        return render_template("dashboard.html") 

@report_bp.route("/save-report", methods=["POST"])
def save_report():
    #filename = request.form.get("filename")
    hemoglobin = request.form.get("hb_value")
    doctor_note = request.form.get("doctor_note")
    report_date = request.form.get("report_date")
    try:
        report = ReportService.save_report(hemoglobin, doctor_note, report_date)
        flash(f"Report saved successfully! Category: {report.category}", "success")
        return redirect(url_for("user.dashboard"))
    except Exception as e:
        flash(f"Error saving report: {e}", "error")
        return redirect(url_for("user.dashboard"))

@report_bp.route("/my-reports", methods=["GET"])
def my_reports():
    hematology_reports, other_reports = ReportService.get_user_reports()

    return render_template(
        "my_reports.html",
        hematology_reports=hematology_reports,
        other_reports=other_reports
    )

@report_bp.route("/hb-analytics", methods=["GET"])
def hb_analytics():
    return render_template("hb_analytics.html")

@report_bp.route("/delete/<int:report_id>", methods=["POST", "GET"])
def delete_report(report_id):
    success = ReportService.delete_report(report_id=report_id)

    if success:
        flash("Report deleted successfully.", "success")
    else:
        flash("Could not delete report. Report may not exist or belong to you.", "danger")
    return redirect(url_for("report.my_reports"))