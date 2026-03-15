import os
import pickle
import random
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
from .diet_suggestions import DIET_SUGGESTIONS
from .health_tips import HEALTH_TIPS

class NutrientDeficiencyUtil:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "deficiency_model.pkl")

    # -----------------------------
    # 1️⃣ Load trained Random Forest model
    # -----------------------------
    with open(MODEL_PATH, "rb") as f:
        model, symptom_cols = pickle.load(f)
    model: RandomForestClassifier

    # -----------------------------
    # 2️⃣ Initialize embedding model
    # -----------------------------
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    # -----------------------------
    # 3️⃣ Canonical symptom list
    # -----------------------------
    SYMPTOMS = symptom_cols  # Ensures embedding vector and RF columns match exactly

    symptom_embeddings = embedding_model.encode(
        [s.lower() for s in SYMPTOMS], normalize_embeddings=True
    )

    # -----------------------------
    # 4️⃣ Map free-text input to symptom vector
    # -----------------------------
    @staticmethod
    def map_input_to_symptom_vector(user_text, threshold=0.5):
        """
        Converts free-text input into a binary vector over canonical symptoms
        """
        user_embedding = NutrientDeficiencyUtil.embedding_model.encode(
            [user_text.lower()], normalize_embeddings=True
        )

        sims = pd.Series(
            data=cosine_similarity(user_embedding, NutrientDeficiencyUtil.symptom_embeddings)[0],
            index=NutrientDeficiencyUtil.SYMPTOMS
        )

        vector = [1 if s >= threshold else 0 for s in sims]

        return vector

    # -----------------------------
    # 5️⃣ Predict deficiencies + probabilities
    # -----------------------------
    @staticmethod
    def predict_top_deficiencies(user_text, top_n=3, threshold=0.5):
        """
        Returns top N predicted deficiencies and full probability list for graphing
        """
        vector = NutrientDeficiencyUtil.map_input_to_symptom_vector(user_text, threshold)
        vector_df = pd.DataFrame([vector], columns=NutrientDeficiencyUtil.SYMPTOMS)

        probs = NutrientDeficiencyUtil.model.predict_proba(vector_df)[0]
        classes = NutrientDeficiencyUtil.model.classes_

        results = [
            {"deficiency": d, "confidence": round(float(p) * 100, 1)}
            for d, p in zip(classes, probs)
        ]

        results_sorted = sorted(results, key=lambda x: x["confidence"], reverse=True)
        top_results = results_sorted[:top_n]

        return top_results, results_sorted

        
    @staticmethod
    def get_diet_suggestions(deficiency_name):
        return DIET_SUGGESTIONS.get(deficiency_name, [])
    
    @staticmethod
    def get_health_tips():
        random_number = random.randint(0, len(HEALTH_TIPS)-1)
        return HEALTH_TIPS[random_number]