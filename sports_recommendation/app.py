# Sports Recommendation Backend with Flask

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory

# Data Preparation
data = {
    "Age": [25, 30, 35, 20, 15, 40, 50],
    "BMI": [22.5, 27.8, 30.2, 20.1, 18.5, 25.6, 28.9],
    "Goal": ["fitness", "weight loss", "muscle gain", "recreation", "team building", "stress relief", "competition"],
    "Preference": ["indoor", "outdoor", "indoor", "outdoor", "outdoor", "indoor", "outdoor"],
    "Recommended Sport": ["yoga", "running", "gym", "basketball", "football", "pilates", "tennis"],
}


df = pd.DataFrame(data)
label_encoders = {}
for col in ["Goal", "Preference", "Recommended Sport"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

X = df.drop("Recommended Sport", axis=1)
y = df["Recommended Sport"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, y_train)

joblib.dump(model, "sports_recommendation_model.pkl")
for col, le in label_encoders.items():
    joblib.dump(le, f"{col}_encoder.pkl")

app = Flask(__name__)
CORS(app)

model = joblib.load("sports_recommendation_model.pkl")
label_encoders = {col: joblib.load(f"{col}_encoder.pkl") for col in ["Goal", "Preference", "Recommended Sport"]}

@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Sports Recommendation System API!"

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    try:
        age = int(data.get("age", 0))
        bmi = float(data.get("bmi", 0))
        goal = data.get("goal", "").lower()
        preference = data.get("preference", "").lower()

        # Validate inputs
        if age < 10 or age > 100:
            return jsonify({"error": "Age must be between 10 and 100."}), 400
        if bmi < 10 or bmi > 60:
            return jsonify({"error": "BMI must be between 10 and 60."}), 400
        
        # handled extreme cases 
        if age > 70:
            return jsonify({"recommended_sport": "Walking, yoga, or light stretching for older individuals."})
        elif bmi > 40:
            return jsonify({"recommended_sport": "Swimming or yoga as low-impact activities."})
        
        # Age-Specific Recommendations
        if age <= 15:
            if preference == "outdoor":
                return jsonify({"recommended_sport": "Football or basketball to encourage teamwork."})
            else:
                return jsonify({"recommended_sport": "Gymnastics or dance for indoor activities."})
        elif 16 <= age <= 30:
            if goal in ["fitness", "muscle gain"]:
                return jsonify({"recommended_sport": "Gym or weight training."})
            elif goal in ["stress relief", "recreation"]:
                return jsonify({"recommended_sport": "Yoga or pilates for relaxation."})
            elif preference == "outdoor":
                return jsonify({"recommended_sport": "Running or cycling for endurance."})
            else:
                return jsonify({"recommended_sport": "Indoor rock climbing for an active workout."})
        elif 31 <= age <= 50:
            if goal in ["weight loss", "stress relief"]:
                return jsonify({"recommended_sport": "Yoga or swimming as low-impact options."})
            elif preference == "outdoor":
                return jsonify({"recommended_sport": "Tennis or golf for outdoor activity."})
            else:
                return jsonify({"recommended_sport": "Pilates or Zumba for indoor fun."})

        # Prepare input data for model
        input_data = pd.DataFrame([{
            "Age": age,
            "BMI": bmi,
            "Goal": label_encoders["Goal"].transform([goal])[0],
            "Preference": label_encoders["Preference"].transform([preference])[0]
        }])

        # Get prediction
        prediction = model.predict(input_data)[0]
        sport = label_encoders["Recommended Sport"].inverse_transform([prediction])[0]
        # Adjust Recommendations for Context
        if preference == "indoor" and sport in ["football", "tennis", "running"]:
            sport = "yoga"
        elif preference == "outdoor" and sport in ["yoga", "gym", "pilates"]:
            sport = "football"

        return jsonify({"recommended_sport": sport})    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)