import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import io
import base64
import plotly.graph_objects as go
import plotly.io as pio

class HbPredictionUtil:

    @staticmethod
    def predict_hb_and_graph(reports, future_days=30):

        if len(reports) < 2:
            raise ValueError("At least 2 reports required for prediction")

        data = {
            "Date": [r.report_date for r in reports],
            "Hb": [float(r.hemoglobin) for r in reports]
        }

        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        df["Days"] = (df["Date"] - df["Date"].min()).dt.days

        X = df[["Days"]]
        y = df["Hb"]

        model = LinearRegression()
        model.fit(X, y)
        # Linear regression slope (gm/dL per day)
        slope_per_day = model.coef_[0]

        # Convert to gm/dL per week
        slope_per_week = slope_per_day * 7
        slope_per_week = round(slope_per_week, 2)

        # Predict future Hb
        future_df = pd.DataFrame([[future_days]], columns=["Days"])
        predicted_hb = model.predict(future_df)[0]
        anemia_type = HbPredictionUtil.classify_anemia(predicted_hb)
        symptoms = HbPredictionUtil.get_symptoms(anemia_type)
        diet_suggestions = HbPredictionUtil.get_diet_suggestions(anemia_type)

        # ---- Create future prediction date ----
        future_date = df["Date"].min() + pd.Timedelta(days=future_days)

        # Trend prediction values
        df["Trend"] = model.predict(X)

        fig = go.Figure()

        # Observed Hb values
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Hb"],
            mode="markers+lines",
            name="Observed Hb",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=9)
        ))

        # Regression trend line
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Trend"],
            mode="lines",
            name="Trend",
            line=dict(color="red", width=3, dash="dash")
        ))

        # Predicted future point
        fig.add_trace(go.Scatter(
            x=[future_date],
            y=[predicted_hb],
            mode="markers",
            name="Predicted Hb",
            marker=dict(
                size=16,
                color="green",
                symbol="star"
            )
        ))

        # Line connecting last point to prediction
        fig.add_trace(go.Scatter(
            x=[df["Date"].iloc[-1], future_date],
            y=[df["Hb"].iloc[-1], predicted_hb],
            mode="lines",
            name="Prediction Path",
            line=dict(color="green", dash="dot")
        ))

        # Normal Hb range shading
        fig.add_shape(
            type="rect",
            x0=df["Date"].min(),
            x1=future_date,
            y0=12,
            y1=16,
            fillcolor="rgba(0,200,0,0.08)",
            line=dict(width=0),
            layer="below"
        )

        # Anemia threshold line
        fig.add_hline(
            y=12,
            line_dash="dash",
            line_color="orange",
            annotation_text="Anemia Threshold",
            annotation_position="top left"
        )

        fig.update_layout(
            title="Hemoglobin Trend & Prediction",
            xaxis_title="Report Date",
            yaxis_title="Hemoglobin (g/dL)",
            template="plotly_white",
            hovermode="x unified",
            height=520,
            legend=dict(
                orientation="h",
                y=1.02,
                x=1,
                xanchor="right"
            ),
        )

        graph_html = pio.to_html(fig, full_html=False)

        risk = "Yes" if predicted_hb < 12 else "No"

        return {
            "predicted_hb": round(predicted_hb, 1),
            "risk": risk,
            "anemia_type": anemia_type,
            "symptoms": symptoms,
            "diet_suggestions": diet_suggestions,
            "graph": graph_html,
            "slope_per_week": slope_per_week
        }
    
    @staticmethod
    def classify_anemia(hb_value):
        try:
            hb = float(hb_value)

            if hb >= 12:
                return "Normal"
            elif 10 <= hb < 12:
                return "Mild Anemia"
            elif 7 <= hb < 10:
                return "Moderate Anemia"
            elif 4 <= hb < 7:
                return "Severe/Serious Anemia"
            elif hb < 4:
                return "Life-threatening Anemia"
            else:
                return "Unknown"
        except:
            return "Invalid Hb value"
    
    @staticmethod
    def get_symptoms(anemia_type):
        symptoms = {
            "Normal": ["No significant symptoms expected"],
            "Mild Anemia": ["Fatigue", "Mild weakness", "Occasional dizziness"],
            "Moderate Anemia": ["Persistent fatigue", "Shortness of breath", "Headaches", "Pale skin"],
            "Severe/Serious Anemia": ["Extreme fatigue", "Chest pain", "Rapid heartbeat", "Dizziness or fainting"],
            "Life-threatening Anemia": ["Severe weakness", "Difficulty breathing", "Confusion", "Possible loss of consciousness"]
        }
        return symptoms.get(anemia_type, [])

    @staticmethod
    def get_diet_suggestions(anemia_type):
        diets = {
            "Normal": ["Maintain a balanced diet rich in iron, vitamins, and protein"],
            "Mild Anemia": ["Leafy green vegetables (spinach, kale)", "Iron-fortified cereals", "Lean meats", "Legumes"],
            "Moderate Anemia": ["Red meat (beef, liver)", "Eggs", "Beans and lentils", "Vitamin C-rich fruits to aid iron absorption"],
            "Severe/Serious Anemia": ["Iron supplements (as prescribed)", "Red meat and liver", "Eggs", "Green leafy vegetables", "Vitamin C-rich fruits"],
            "Life-threatening Anemia": ["Immediate medical attention required", "Iron-rich foods and supplements under supervision"]
        }
        return diets.get(anemia_type, ["Consult a doctor for dietary advice"])