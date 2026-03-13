import os
import pickle
import random
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from .diet_suggestions import DIET_SUGGESTIONS
from .health_tips import HEALTH_TIPS

class NutrientDeficiencyUtil:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "synthetic_deficiency_embeddings.pkl")

    with open(MODEL_PATH, "rb") as f:
        df = pickle.load(f)

    SYMPTOM_KEYWORDS = {
        "tired": "Fatigue",
        "fatigue": "Fatigue",
        "weak": "Fatigue",
        "pins and needles": "Tingling Sensation",
        "tingling": "Tingling Sensation",
        "night blindness": "Night Blindness",
        "dry eyes": "Dry Eyes",
        "bleeding gums": "Bleeding Gums",
        "low sun exposure": "Low Sun Exposure",
        "reduced memory": "Reduced Memory Capacity",
        "shortness of breath": "Shortness of Breath",
        "loss of appetite": "Loss of Appetite",
        "fast heart rate": "Fast Heart Rate",
        "brittle nails": "Brittle Nails",
        "weight loss": "Weight Loss",
        "reduced wound healing": "Reduced Wound Healing Capacity",
        "skin condition": "Skin Condition"
    }

    symptom_cols = [
        "Night Blindness", "Dry Eyes", "Bleeding Gums", "Fatigue", "Tingling Sensation",
        "Low Sun Exposure", "Reduced Memory Capacity", "Shortness of Breath",
        "Loss of Appetite", "Fast Heart Rate", "Brittle Nails", "Weight Loss",
        "Reduced Wound Healing Capacity", "Skin Condition"
    ]

    @staticmethod
    def map_input_to_vector(user_text):
        user_text = user_text.lower()
        user_vector = []

        for col in NutrientDeficiencyUtil.symptom_cols:
            matched = False
            for keyword, col_name in NutrientDeficiencyUtil.SYMPTOM_KEYWORDS.items():
                if keyword in user_text and col_name.lower() == col.lower():
                    matched = True
                    break
            user_vector.append(1 if matched else 0)

        return user_vector

    @staticmethod
    def predict_top_deficiencies(user_input, top_n=3):
        user_vector = NutrientDeficiencyUtil.map_input_to_vector(user_input)
        dataset_vectors = NutrientDeficiencyUtil.df[NutrientDeficiencyUtil.symptom_cols].values
        sims = cosine_similarity([user_vector], dataset_vectors)[0]

        # Create DataFrame with similarity and deficiency
        df_sim = NutrientDeficiencyUtil.df[["Predicted Deficiency"]].copy()
        df_sim["Similarity"] = sims

        # Take max similarity per unique deficiency
        df_grouped = df_sim.groupby("Predicted Deficiency", as_index=False).agg({"Similarity": "max"})

        # Sort and take top N unique deficiencies
        df_top = df_grouped.sort_values("Similarity", ascending=False).head(top_n)

        results = []
        for _, row in df_top.iterrows():
            results.append({
                "deficiency": row["Predicted Deficiency"],
                "similarity": round(float(row["Similarity"]) * 100, 1)
            })

        return results, sims
    
    @staticmethod
    def get_diet_suggestions(deficiency_name):
        return DIET_SUGGESTIONS.get(deficiency_name, [])
    
    @staticmethod
    def get_health_tips():
        random_number = random.randint(0, len(HEALTH_TIPS))
        return HEALTH_TIPS[random_number]