from flask import Blueprint, render_template

report_bp = Blueprint("report", __name__)

@report_bp.route("/validate")
def validate():
    return render_template("validate.html")