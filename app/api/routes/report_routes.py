from flask import Blueprint, render_template

report_bp = Blueprint("report", __name__)

@report_bp.route("/validate")
def validate():
    return render_template("validate.html")

@report_bp.route("/blur_analysis")
def blur_analysis():
    return render_template("blur_analysis.html", variance_value=369.98, threshold=100)