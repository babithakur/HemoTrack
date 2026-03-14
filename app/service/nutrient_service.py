from app.utils.nutrient_deficiency_util import NutrientDeficiencyUtil
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd

class NutrientService:

    @staticmethod
    def predict_nutrient_deficiency(symptoms, top_n=3, max_bars=10):
        """
        Predict nutrient deficiencies and generate similarity graph
        """
        if not symptoms:
            raise ValueError("Symptoms input required")

        # Top predictions
        top_results, sims = NutrientDeficiencyUtil.predict_top_deficiencies(symptoms, top_n=top_n)
        # After predicting top deficiencies
        primary_deficiency = top_results[0]["deficiency"]  # top predicted nutrient
        diet_plan = [
            {"deficiency": d["deficiency"], "plan": NutrientDeficiencyUtil.get_diet_suggestions(d["deficiency"])}
            for d in top_results
        ]
        health_tip = NutrientService.fetch_health_tips()

        # Aggregate similarities by unique deficiency
        df_sims = pd.DataFrame({
            "Deficiency": NutrientDeficiencyUtil.df["Predicted Deficiency"],
            "Similarity": sims
        })
        df_grouped = df_sims.groupby("Deficiency", as_index=False).agg({"Similarity": "max"})
        df_top = df_grouped.sort_values("Similarity", ascending=False).head(max_bars)

        # Dynamic height (50px per bar, min 400px)
        #chart_height = max(400, len(df_top) * 50)

        # Horizontal bar chart
        fig = go.Figure(go.Bar(
            x=df_top["Similarity"] * 100,
            y=df_top["Deficiency"],
            orientation='h',
            marker=dict(color='teal')
        ))

        fig.update_layout(
            title=dict(
                text="Similarity Scores with Known Deficiency Profiles",
                x=0.5,
                xanchor='center',
            ),
            height=440,
            margin=dict(l=80, r=20, t=90, b=50),
            yaxis=dict(autorange="reversed"),
            template="plotly_white"
        )

        # Convert to HTML for embedding
        graph_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'responsive': True})

        return {
            "symptoms": symptoms,
            "top_deficiencies": top_results,
            "diet_plan": diet_plan,
            "health_tip": health_tip,
            "graph_html": graph_html
        }
    
    @staticmethod
    def fetch_health_tips():
        return NutrientDeficiencyUtil.get_health_tips()