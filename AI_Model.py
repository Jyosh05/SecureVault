import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score

# Load the dataset from the JSON file
with open('./test_data/pii_data.json', 'r') as json_file:
    data = json.load(json_file)

# Convert the data into a pandas DataFrame
df = pd.DataFrame(data)

# Check for missing or invalid data
print(df.head())
print(df.isnull().sum())

X = df['text']  # Text data
y = df['pii_types']  #PII label

#convert PII labels into binary matrix
mlb = MultiLabelBinarizer()
y_bin = mlb.fit_transform(y)

# Check label encoding
print(f"Label classes: {mlb.classes_}")
print(f"First few labels: {y_bin[:5]}")

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)

# Print size of training and test sets
print(f"Training data size: {len(X_train)}")
print(f"Testing data size: {len(X_test)}")

# Create a pipeline with a TfidfVectorizer and a RandomForestClassifier
model = make_pipeline(
    TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english'),
    MultiOutputClassifier(RandomForestClassifier(n_estimators=10, random_state=42))
)

# Train the model
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
f1 = f1_score(y_test, y_pred, average='micro')  # You can also use 'macro' or 'weighted'
print(f"F1 Score: {f1 * 100:.2f}%")

# Save the trained model and MultiLabelBinarizer
joblib.dump(model, 'pii_model.pkl')
joblib.dump(mlb, 'pii_label_encoder.pkl')
print("Model and label encoder saved as 'pii_model.pkl' and 'pii_label_encoder.pkl'")

print("PII Detection Console - Type 'exit' to quit")
while True:
    # Get user input
    user_input = input("Enter text to analyze: ")

    # Exit the loop if the user types "exit"
    if user_input.lower() == 'exit':
        print("Exiting PII Detection Console. Goodbye!")
        break

    # Make predictions using the loaded model
    predicted = model.predict([user_input])

    # Decode the predicted labels
    detected_pii = mlb.inverse_transform(predicted)

    # Display the detected PII types
    if detected_pii[0]:
        print(f"Detected PII Types: {', '.join(detected_pii[0])}")
    else:
        print("No PII detected in the input text.")