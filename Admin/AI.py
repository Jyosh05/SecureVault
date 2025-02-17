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
from flask import request, flash, redirect, url_for, render_template, Blueprint, jsonify
from Utils.rbac_utils import roles_required
from config import MODEL_FILE,LABEL_ENCODER_FILE, DATA_FILE
import os
import fitz


ai_bp = Blueprint('ai',__name__, template_folder='templates')


def load_AI_model():
    global model, mlb
    try:
        model = joblib.load(MODEL_FILE)
        mlb = joblib.load(LABEL_ENCODER_FILE)
    except:
        model = None
        mlb = None


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

    return model, mlb

@ai_bp.route('/update_model', methods=['GET', 'POST'])
@roles_required('so')
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

            # Create new DataFrame
            df_new = pd.DataFrame([new_data])

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


@ai_bp.route('/scan_pdfs', methods=['POST','GET'])
def scan_pdfs():
    load_AI_model()
    if model is None or mlb is None:
        return render_template('Admin/scan_reports.html', pii_detected_files=[], error="Model is not trained yet.")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Files'))
    subdirs = ["Perma", "Redact_&_Watermark", "Soft_Deletion"]
    pii_detected_files = []

    for subdir in subdirs:
        pdf_dir = os.path.join(base_dir, subdir)
        if not os.path.isdir(pdf_dir):
            continue

        for root, _, files in os.walk(pdf_dir):
            for filename in files:
                if filename.endswith('.pdf'):
                    pdf_path = os.path.join(root, filename)

                    try:
                        with fitz.open(pdf_path) as doc:
                            text = " ".join([page.get_text() for page in doc])

                            # Iterate through pages and check for redactions (black boxes)
                            for page_num in range(doc.page_count):
                                page = doc.load_page(page_num)
                                redacted_regions = []  # List to store redacted regions

                                # Check for redaction annotations
                                annotations = page.annots()  # Get annotations on the page
                                if annotations:
                                    for annot in annotations:
                                        if annot.type[0] == 8:  # Check if it's a redaction annotation (type 8)
                                            redacted_regions.append(annot.rect)  # Get the bounding box of the redaction

                                # Remove redacted text from the extracted text
                                page_text = page.get_text("text")
                                for rect in redacted_regions:
                                    page_text = remove_redacted_text(page_text, rect, page)

                                # Perform PII detection on the text that is not redacted
                                if page_text.strip():
                                    prediction = model.predict([page_text])
                                    labels = mlb.inverse_transform(prediction)


                                    if any(labels):
                                        pii_detected_files.append({'file': filename, 'pii_types': labels[0]})

                    except Exception as e:
                        print(f"Error processing {pdf_path}: {e}")


    return render_template('Admin/scan_reports.html', pii_detected_files=pii_detected_files)


def remove_redacted_text(page_text, rect, page):
    """Remove text from redacted regions to ensure PII detection does not consider them."""
    words = page.get_text("words")
    redacted_text = ""

    # Iterate over the words and check if they are inside the redacted rect
    for word in words:
        word_rect = fitz.Rect(word[:4])  # Get the bounding box of the word
        if rect.intersects(word_rect):  # If the word is inside the redacted region
            # Replace redacted text with spaces (to maintain text length)
            redacted_text += " " * len(word[4])  # Add spaces of same length as the word
        else:
            redacted_text += word[4] + " "  # Add non-redacted text normally

    return redacted_text
