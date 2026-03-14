from flask import Blueprint, request, render_template
from app.service.nutrient_service import NutrientService

nutrient_bp = Blueprint("nutrient_bp", __name__)


@nutrient_bp.route("/nutrient-prediction", methods=["GET", "POST"])
def nutrient_prediction():
    result = {"health_tip": NutrientService.fetch_health_tips()}
    symptoms = ""
    if request.method == "POST":
        symptoms = request.form.get("symptoms")
        try:
            result = NutrientService.predict_nutrient_deficiency(symptoms)
        except Exception as e:
            result = {"error": str(e)}
    return render_template("nutrient_prediction.html", result=result, user_input=symptoms)