import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier

# 1. Load Data
df = pd.read_csv("triage_dataset.csv")

# 2. Define Features and Target
# We will use 'symptoms_text' (text), 'age' (numeric), 'fever' (categorical/binary), 'chest_pain' (binary), 'duration_days' (numeric)
X = df[['symptoms_text', 'age', 'fever', 'chest_pain', 'duration_days']]
y = df['specialty']

# 3. Preprocessing
# Text features: specific pipeline (TF-IDF)
# Categorical (fever, chest_pain): OneHotEncoder (or just map yes/no to 1/0 if we cleaned it manually, but OHE is safer)
# Numeric (age, duration_days): Passthrough

# Note: In the API, we manually mapped fever/chest_pain to 0/1. 
# Let's ensure the training data handles 'yes'/'no' correctly or we preprocess it consistently.
# To match the API logic (which sends 0/1), let's map the dataframe here first.
df['fever'] = df['fever'].apply(lambda x: 1 if x == 'yes' else 0)
df['chest_pain'] = df['chest_pain'].apply(lambda x: 1 if x == 'yes' else 0)

# Now X uses the processed numeric columns
X = df[['symptoms_text', 'age', 'fever', 'chest_pain', 'duration_days']]

preprocessor = ColumnTransformer(
    transformers=[
        ('text', TfidfVectorizer(stop_words='english'), 'symptoms_text'),
        ('num', 'passthrough', ['age', 'fever', 'chest_pain', 'duration_days'])
    ]
)

# 4. Model Pipeline
# Using RandomForest as it handles mixed numeric/text features decently after vectorization
model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# 5. Train
print("Training model...")
model.fit(X, y)
print("Model training complete.")

# 6. Save Model
joblib.dump(model, "triage_model.pkl")
print("Model saved as 'triage_model.pkl'")
