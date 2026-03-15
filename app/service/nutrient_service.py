from app.utils.nutrient_deficiency_util import NutrientDeficiencyUtil
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd

class NutrientService:

    @staticmethod
    def predict_nutrient_deficiency(symptoms, top_n=3, max_bars=10, threshold=0.5):
        if not symptoms:
            raise ValueError("Symptoms input required")

        # Get predictions and probabilities
        top_results, all_results = NutrientDeficiencyUtil.predict_top_deficiencies(
            symptoms, top_n=top_n, threshold=threshold
        )

        primary_deficiency = top_results[0]["deficiency"] if top_results else None

        diet_plan = [
            {
                "deficiency": d["deficiency"],
                "plan": NutrientDeficiencyUtil.get_diet_suggestions(d["deficiency"])
            }
            for d in top_results
        ]

        health_tip = NutrientService.fetch_health_tips()

        # Build dataframe for graph
        df_probs = pd.DataFrame(all_results)
        df_top = df_probs.sort_values("confidence", ascending=False).head(max_bars)

        # Horizontal bar chart with confidence on bars
        fig = go.Figure(go.Bar(
            x=df_top["confidence"],
            y=df_top["deficiency"],
            orientation='h',
            text=df_top["confidence"].astype(str) + "%",
            textposition="outside",
            marker=dict(color='teal')
        ))

        fig.update_layout(
            title=dict(
                text="Predicted Nutrient Deficiency Confidence",
                x=0.5,
                xanchor='center'
            ),
            height=420,
            margin=dict(l=10, r=10, t=90, b=50),
            yaxis=dict(autorange="reversed"),
            template="plotly_white"
        )

        fig.update_traces(
            marker=dict(color='teal', line=dict(width=0)),
            textposition='inside',
            textfont=dict(size=10)  # smaller text labels
        )

        graph_html = pio.to_html(
            fig,
            full_html=False,
            include_plotlyjs='cdn',
            config={'responsive': True}
        )

        return {
            "symptoms": symptoms,
            "primary_deficiency": primary_deficiency,
            "top_deficiencies": top_results,
            "diet_plan": diet_plan,
            "health_tip": health_tip,
            "graph_html": graph_html
        }
        
    @staticmethod
    def fetch_health_tips():
        return NutrientDeficiencyUtil.get_health_tips()