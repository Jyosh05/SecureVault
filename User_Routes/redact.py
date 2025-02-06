import spacy
import fitz  # PyMuPDF
import re
import joblib
import numpy as np
from flask import Blueprint, render_template, request, send_file, url_for, flash, redirect
from werkzeug.utils import secure_filename
from Utils.general_utils import make_dir_for_temp_upload, allowed_file
from Utils.PDF_Redaction import redact_pdf
from Utils.rbac_utils import roles_required, role_redirects
from config import MODEL_FILE, LABEL_ENCODER_FILE
import os



# Load spaCy's pre-trained NER model
nlp = spacy.load("en_core_web_sm")

redact_bp = Blueprint('redact', __name__, template_folder='templates')


@redact_bp.route('/redact')
@roles_required('patient', 'doctor')
def redact():
    return render_template('Features/PDF_Redactor.html', role_redirects=role_redirects)


# Function to detect named entities using spaCy NER
def detect_entities(text):
    doc = nlp(text)  # Process the text with spaCy's NER model
    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))  # Return text and label of the entity
    return entities


# Function to redact detected PII using NER and regex patterns
def redact_pii_using_ner(doc):
    found_pii = False  # Flag to track if any PII is detected
    redacted_pdf_path = "path_to_save_redacted_pdf.pdf"  # Define path for redacted file

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")
        print(f"Extracted text from page {page_num + 1}: {page_text[:500]}")  # Print first 500 characters for preview

        # Detect named entities in the page text
        entities = detect_entities(page_text)
        print(f"Detected entities on page {page_num + 1}: {entities}")

        # Redact detected names (PERSON entities)
        for entity, label in entities:
            if label == "PERSON":
                print(f"Found name: {entity} on page {page_num + 1}")
                words = page.get_text("words")
                for word in words:
                    if entity in word[4]:
                        rect = fitz.Rect(word[:4])  # Get rectangle coordinates for the word
                        print(f"Redacting name at rect: {rect}")
                        page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))  # Redact the entity
                        found_pii = True

        # Regex for NRIC numbers (Singapore format)
        nric_pattern = r"^[STFG]\d{7}[A-Z]$"
        for match in re.finditer(nric_pattern, page_text):
            print(f"Found NRIC match: {match.group(0)} on page {page_num + 1}")
            words = page.get_text("words")
            for word in words:
                if match.group(0) in word[4]:
                    rect = fitz.Rect(word[:4])
                    print(f"Redacting NRIC at rect: {rect}")
                    page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))
                    found_pii = True

    if found_pii:
        doc.save(redacted_pdf_path)
        doc.close()
        print(f"Redaction completed and saved to: {redacted_pdf_path}")
    else:
        doc.close()
        print("No PII detected.")

    return redacted_pdf_path


@redact_bp.route('/redact_upload', methods=['POST'])
@roles_required('patient')
def redact_upload():
    try:
        model = joblib.load(MODEL_FILE)
        mlb = joblib.load(LABEL_ENCODER_FILE)
        print("AI model and label encoder loaded successfully.")
    except FileNotFoundError:
        flash("AI model not found. Please train the model first.", "error")
        return redirect(url_for('ai.update_model'))

    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('redact.redact'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('redact.redact'))

    if not allowed_file(file.filename):
        flash('Unsupported file type. Please upload a valid file.', 'error')
        return redirect(url_for('redact.redact'))

    filename = secure_filename(file.filename)
    temp_upload_folder = make_dir_for_temp_upload()

    temp_file_path = os.path.join(temp_upload_folder, filename)
    file.save(temp_file_path)
    print("File saved to:", temp_file_path)

    redacted_pdf_path = os.path.join(temp_upload_folder, f'redacted_{filename}')
    print("Redacted PDF will be saved to:", redacted_pdf_path)

    found_pii = False  # Flag to track if any PII is detected by the AI

    # Use AI for PII detection and redaction if available
    if model is not None and mlb is not None:
        doc = fitz.open(temp_file_path)
        print("Opened PDF document. Number of pages:", doc.page_count)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            print(f"Processing page {page_num + 1}.")
            print("Extracted text from page:", page_text)

            # Get the prediction for the current page
            predicted_labels = model.predict([page_text])
            print("Raw predicted_labels from model:", predicted_labels)

            # Convert to a NumPy array to ensure it has a .shape attribute
            predicted_labels = np.array(predicted_labels)
            print("Predicted labels as NumPy array with shape", predicted_labels.shape)

            # Inverse transform to get the original labels
            predicted_labels = mlb.inverse_transform(predicted_labels)
            print("Predicted labels after inverse_transform:", predicted_labels)

            # Check if any key PII label is present.
            if predicted_labels and any(label in predicted_labels[0] for label in
                                        ["Credit Card Number", "Social Security Number", "Phone", "Email", "Address"]):
                print("PII detected on page", page_num + 1)
                found_pii = True  # Mark that we've detected PII on at least one page

                # Regex patterns for PII
                credit_card_patterns = [
                    r"^\d{4}-\d{4}-\d{4}-\d{4}$",  # Format: XXXX-XXXX-XXXX-XXXX
                    r"^\d{16}$"  # Format: 16 digits without separators
                ]
                phone_number_patterns = [
                    r"^\+?\d{10,15}$",  # International format with optional +
                    r"^\d{3}-\d{3}-\d{4}$",  # US format: XXX-XXX-XXXX
                    r"^\d{10}$"  # 10-digit phone number
                ]

                # Redact credit card numbers
                for pattern in credit_card_patterns:
                    for match in re.finditer(pattern, page_text):
                        print(f"Found credit card match: {match.group(0)} on page {page_num + 1}")
                        words = page.get_text("words")
                        for word in words:
                            if match.group(0) in word[4]:
                                rect = fitz.Rect(word[:4])
                                print(f"Redacting credit card at rect: {rect}")
                                page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))

                # Redact phone numbers
                for pattern in phone_number_patterns:
                    for match in re.finditer(pattern, page_text):
                        print(f"Found phone number match: {match.group(0)} on page {page_num + 1}")
                        words = page.get_text("words")
                        for word in words:
                            if match.group(0) in word[4]:
                                rect = fitz.Rect(word[:4])
                                print(f"Redacting phone number at rect: {rect}")
                                page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))

        if found_pii:
            doc.save(redacted_pdf_path)
            doc.close()
            print("Redaction completed using AI and saved to:", redacted_pdf_path)
        else:
            doc.close()
            print("No PII detected by AI in any page. Falling back to PDF redactor function.")
            redact_pdf(temp_file_path, redacted_pdf_path)
    else:
        print("Model or label encoder not available, using fallback redaction.")
        redact_pdf(temp_file_path, redacted_pdf_path)

    return send_file(redacted_pdf_path, as_attachment=True, download_name=f"redacted_{filename}")
