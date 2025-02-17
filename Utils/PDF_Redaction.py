import fitz  # PyMuPDF
import re
import spacy


def redact_pdf(input_pdf_path, output_pdf_path):
    """Redact personal information in a PDF using regex and named entity recognition (NER) for names."""

    # Define regex patterns for personal information
    patterns = {
        "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
        "nric": r"\b[A-Z]\d{7}[A-Z]\b",
        "name": r"\b[A-Z][a-z]* [A-Z][a-z]*\b",
        "location": r"\b[A-Z][a-z]*, [A-Z][a-z]*\b",
        "gmail": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    }

    # Load English NLP model for NER (named entity recognition)
    nlp = spacy.load("en_core_web_sm")

    # Open the input PDF
    doc = fitz.open(input_pdf_path)

    # Iterate through each page
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")

        # Regex-based redaction (for PII)
        for label, pattern in patterns.items():
            matches = re.finditer(pattern, page_text)
            for match in matches:
                bbox = match.span()
                words = page.get_text("words")
                for word in words:
                    if match.group(0) in word[4]:  # Word is at the right position
                        # Draw a black rectangle over the match
                        rect = fitz.Rect(word[:4])  # x0, y0, x1, y1 for word bounding box
                        page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))  # Black out

        # Named Entity Recognition-based redaction (for names)
        spacy_doc = nlp(page_text)  # Process text with spaCy
        for ent in spacy_doc.ents:
            if ent.label_ == "PERSON":  # Only redact names
                redaction_rects = page.search_for(ent.text)
                for rect in redaction_rects:
                    page.add_redact_annot(rect, fill=(0, 0, 0))

        # Apply all redactions for the page
        page.apply_redactions()

    # Save the redacted PDF
    doc.save(output_pdf_path)
    doc.close()









