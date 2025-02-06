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
from flask import request, flash, redirect, url_for, render_template, Blueprint
from Utils.rbac_utils import roles_required
from config import MODEL_FILE,LABEL_ENCODER_FILE, DATA_FILE

ai_bp = Blueprint('ai',__name__, template_folder='templates')


def load_AI_model():
    global model, mlb
    try:
        model = joblib.load(MODEL_FILE)
        mlb = joblib.load(LABEL_ENCODER_FILE)
        print("model is loaded")
    except:
        model = None
        mlb = None
        print("no existing model, will train on the first update")

def train_model(df):
    X = df['text']
    y = df['pii_types']

    mlb = MultiLabelBinarizer()
    y_bin = mlb.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)

    model = make_pipeline(
        TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english'),
        MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred, average='micro')
    print(f"F1 Score: {f1 * 100:.2f}%")

    joblib.dump(model, MODEL_FILE)
    joblib.dump(mlb, LABEL_ENCODER_FILE)
    print(f"Model and label encoder saved to {MODEL_FILE} and {LABEL_ENCODER_FILE}")
    return model, mlb

@ai_bp.route('/update_model', methods=['GET', 'POST'])
def update_model():
    load_AI_model()  # Load existing model if available
    if request.method == 'POST':
        try:
            # Read existing data (if available)
            try:
                existing_df = pd.read_json(DATA_FILE)
            except FileNotFoundError:
                existing_df = pd.DataFrame(columns=['text', 'pii_types', 'label'])

            # Get keyword data from the form
            text_data = request.form.get('text')
            pii_types = request.form.getlist('pii_types[]')
            label = 1 if pii_types else 0  # Set label based on PII types

            # Create new data dictionary
            new_data = {
                'text': text_data,
                'pii_types': pii_types,
                'label': label,
            }

            print(new_data)
            # Create new DataFrame
            df_new = pd.DataFrame([new_data])
            print(df_new)

            # Concatenate existing and new data
            df = pd.concat([existing_df, df_new], ignore_index=True)

            # Save combined data
            df.to_json(DATA_FILE, orient='records', indent=4)

            # Retrain model
            global model, mlb
            model, mlb = train_model(df)  # Retrain model

            flash('Model updated successfully!', 'success')
            return redirect(url_for('ai.update_model'))

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            flash(f'Error processing data: {e}', 'error')
            return render_template('Admin/update_model.html')

    return render_template('Admin/update_model.html')