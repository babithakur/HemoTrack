from app.utils.nutrient_deficiency_util import NutrientDeficiencyUtil
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd

class NutrientService:

    @staticmethod
    def predict_nutrient_deficiency(symptoms, top_n=3, max_bars=10, threshold=0.5):
        if not symptoms:
            raise ValueError("Symptoms input required")

        response = NutrientDeficiencyUtil.predict_top_deficiencies(
            symptoms, top_n=top_n, threshold=threshold
        )

        top_results = response["predictions"]
        all_results = response["all_probabilities"]
        metrics = response["metrics"]

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

        # --------------------------
        # Heatmap for confusion matrix
        # --------------------------
        if "confusion_matrix" in metrics and "labels" in metrics:
            fig_cm = go.Figure(
                data=go.Heatmap(
                    z=metrics["confusion_matrix"],
                    x=metrics["labels"],
                    y=metrics["labels"],
                    colorscale='Blues',
                    showscale=True,
                    text=metrics["confusion_matrix"],
                    texttemplate="%{text}",
                )
            )
            fig_cm.update_layout(
                title=dict(text="Model Confusion Matrix", x=0.5, xanchor='center'),
                xaxis_title="Predicted",
                yaxis_title="Actual",
                template="plotly_white",
                height=450,
            )
            graph_cm_html = pio.to_html(fig_cm, full_html=False, include_plotlyjs='cdn', config={'responsive': True})
        else:
            graph_cm_html = None

        return {
            "symptoms": symptoms,
            "primary_deficiency": primary_deficiency,
            "top_deficiencies": top_results,
            "diet_plan": diet_plan,
            "health_tip": health_tip,
            "graph_confusion_matrix_html": graph_cm_html,
            "graph_html": graph_html,
            "metrics": metrics
        }
        
    @staticmethod
    def fetch_health_tips():
        return NutrientDeficiencyUtil.get_health_tips()