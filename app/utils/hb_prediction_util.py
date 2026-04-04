import pandas as pd
import matplotlib.pyplot as plt
##from sklearn.linear_model import LinearRegression
from .linear_regression import SimpleLinearRegression
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

        ##model = LinearRegression()
        ##model.fit(X, y)

        model = SimpleLinearRegression()
        model.fit(X["Days"], y)
        # Linear regression slope (gm/dL per day)
        ##slope_per_day = model.coef_[0]
        slope_per_day = model.coef_

        # Convert to gm/dL per week
        ##slope_per_week = slope_per_day * 7
        ##slope_per_week = round(slope_per_week, 2)
        slope_per_week = round(slope_per_day * 7, 2)

        # Predict future Hb
        ##future_df = pd.DataFrame([[future_days]], columns=["Days"])
        ##predicted_hb = model.predict(future_df)[0]
        ###predicted_hb = model.predict([future_days])[0]
        ##anemia_type = HbPredictionUtil.classify_anemia(predicted_hb)
        ##symptoms = HbPredictionUtil.get_symptoms(anemia_type)
        ##diet_suggestions = HbPredictionUtil.get_diet_suggestions(anemia_type)

        last_day = df["Days"].max()
        future_day_value = last_day + future_days

        predicted_hb_reg = model.predict([future_day_value])[0]
        predicted_hb = predicted_hb_reg
        predicted_hb_ma = df["Hb"].tail(3).mean()

        # ---- Create future prediction date ----
        ###future_date = df["Date"].min() + pd.Timedelta(days=future_days)
        last_date = df["Date"].max()
        future_date = last_date + pd.Timedelta(days=future_days)

        # Trend prediction values
        ##df["Trend"] = model.predict(X)
        ###df["Trend"] = model.predict(df["Days"])
        df["Trend"] = model.predict(df["Days"].values)

        # Metrics
        mse = model.mse(df["Days"], y)
        r2 = model.r2_score(df["Days"], y)
        rmse = np.sqrt(mse)

        baseline_pred = df["Hb"].iloc[-1]
        baseline_mse = np.mean((y - baseline_pred) ** 2)

        # Default prediction (regression)
        ###predicted_hb_reg = model.predict([future_days])[0]

        # ---- SMART DECISION LOGIC ----

        confidence = "High"
        warning = None


        # Rule 1: Too little data
        if len(df) < 4:
            predicted_hb = df["Hb"].iloc[-1]  # fallback to latest
            confidence = "Low"
            warning = "Very limited data. Prediction based on latest value."

        # Rule 2: Weak trend
        elif r2 < 0.5:
            predicted_hb = df["Hb"].iloc[-1]
            confidence = "Low"
            warning = "Hb trend is unstable. Prediction may not be reliable."
        
        # Rule 4: Large jump (VERY important for your case)
        elif abs(predicted_hb_reg - df["Hb"].iloc[-1]) > 1.0:
            predicted_hb = (predicted_hb_reg + df["Hb"].iloc[-1]) / 2
            confidence = "Medium"
            warning = "Large jump detected. Prediction smoothed."
        
        elif mse > baseline_mse:
            predicted_hb = baseline_pred
            confidence = "Low"
            warning = "Model performs worse than baseline (last value)."
        
        # Rule 3: High error
        elif rmse > 1.0:
            predicted_hb = (predicted_hb_reg + predicted_hb_ma) / 2
            confidence = "Medium"
            warning = "Prediction adjusted due to high variability."

        # Rule 4: Good model
        else:
            predicted_hb = predicted_hb_reg
            confidence = "High"
        
        if rmse > 1.0:
            max_change = 0.8
        else:
            max_change = 1.2

        last_hb = df["Hb"].iloc[-1]
        delta = predicted_hb - last_hb

        if abs(delta) > max_change:
            predicted_hb = last_hb + np.sign(delta) * max_change
            warning = (warning + " " if warning else "") + "Clamped to realistic biological change."

        anemia_type = HbPredictionUtil.classify_anemia(predicted_hb)
        symptoms = HbPredictionUtil.get_symptoms(anemia_type)
        diet_suggestions = HbPredictionUtil.get_diet_suggestions(anemia_type)

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
            "slope_per_week": slope_per_week,
            "mse": round(mse, 2),
            "r2_score": round(r2, 2),
            "rmse": round(rmse, 2),
            "confidence": confidence,
            "warning": warning
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
            "Normal": ["Maintain a balanced diet rich in essential nutrients"],
            "Mild Anemia": ["Leafy green vegetables (spinach, kale)", "Iron-fortified cereals", "Lean meats", "Legumes"],
            "Moderate Anemia": ["Red meat (beef, liver)", "Eggs", "Beans and lentils", "Vitamin C-rich fruits to aid iron absorption"],
            "Severe/Serious Anemia": ["Iron supplements (as prescribed)", "Red meat and liver", "Eggs", "Green leafy vegetables", "Vitamin C-rich fruits"],
            "Life-threatening Anemia": ["Immediate medical attention required", "Iron-rich foods and supplements under supervision"]
        }
        return diets.get(anemia_type, ["Consult a doctor for dietary advice"])