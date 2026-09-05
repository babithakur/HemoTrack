import pandas as pd
import random
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, log_loss
import numpy as np

symptom_cols = [
    "Night Blindness","Dry Eyes","Bleeding Gums","Fatigue","Tingling Sensation",
    "Low Sun Exposure","Reduced Memory Capacity","Shortness of Breath",
    "Cold Hands and Feet","Fast Heart Rate","Brittle Nails","Weight Loss",
    "Reduced Wound Healing Capacity","Skin Condition",
    "Bone Pain and Muscle Weakness","Frequent Infections","Hair Loss",
    "Loss of Appetite"
]

deficiencies = ["Iron","Vitamin A","Vitamin B12","Vitamin C","Zinc","Vitamin D"]

rows = []
N_SAMPLES = 8000

for _ in range(N_SAMPLES):
    deficiency = random.choice(deficiencies)
    symptoms = {col:0 for col in symptom_cols}

    if deficiency == "Iron":
        symptoms.update({
            "Fatigue": random.choice([1]*3 + [0]),
            "Shortness of Breath": random.choice([1,0,0]),
            "Cold Hands and Feet": random.choice([1,0,0]),
            "Brittle Nails": random.choice([1,0,0])
        })
    elif deficiency == "Vitamin A":
        symptoms.update({
            "Night Blindness": random.choice([1,0,0]),  # reduced deterministic
            "Dry Eyes": random.choice([1,0,0]),
            "Frequent Infections": random.choice([1,0,0])
        })
    elif deficiency == "Vitamin B12":
        symptoms.update({
            "Tingling Sensation": random.choice([1,0,0]),
            "Reduced Memory Capacity": random.choice([1,0,0]),
            "Fatigue": random.choice([1,0,0])
        })
    elif deficiency == "Vitamin C":
        symptoms.update({
            "Bleeding Gums": random.choice([1,0,0]),
            "Skin Condition": random.choice([1,0,0]),
            "Reduced Wound Healing Capacity": random.choice([1,0,0])
        })
    elif deficiency == "Zinc":
        symptoms.update({
            "Loss of Appetite": random.choice([1,0,0]),
            "Hair Loss": random.choice([1,0,0]),
            "Weight Loss": random.choice([1,0,0]),
            "Frequent Infections": random.choice([1,0,0])
        })
    elif deficiency == "Vitamin D":
        symptoms.update({
            "Bone Pain and Muscle Weakness": random.choice([1,0,0]),
            "Fatigue": random.choice([1,0,0]),
            "Hair Loss": random.choice([1,0,0])
        })

    for col in symptom_cols:
        if random.random() < 0.05:  # 5% chance to flip any symptom
            symptoms[col] = 1 - symptoms[col]

    row = {**symptoms, "Deficiency": deficiency}
    rows.append(row)

df = pd.DataFrame(rows)
print("Dataset shape:", df.shape)

X = df[symptom_cols]
y = df["Deficiency"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)
pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)
conf_matrix = confusion_matrix(y_test, pred)
top3_acc = np.mean([y_test.iloc[i] in np.array(model.classes_)[np.argsort(model.predict_proba(X_test)[i])[-3:]] for i in range(len(y_test))])
loss = log_loss(y_test, model.predict_proba(X_test))

print("Accuracy:", accuracy)
print("Top-3 Accuracy:", top3_acc)
print("Confusion Matrix:\n", conf_matrix)
print(classification_report(y_test, pred))

metrics = {
    "accuracy": accuracy,
    "top_3_accuracy": top3_acc,
    "confusion_matrix": conf_matrix.tolist()
}

with open("deficiency_model_new.pkl", "wb") as f:
    pickle.dump((model, symptom_cols, metrics), f)

print("Model saved with metrics!")
