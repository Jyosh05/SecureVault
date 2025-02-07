import fitz  # PyMuPDF
import re
import spacy


def redact_pdf(input_pdf_path, output_pdf_path):
    """Redact personal information in a PDF using black rectangles."""
    # Define regex patterns for personal information
    patterns = {
        "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
        "nric": r"\b[A-Z]\d{7}[A-Z]\b",
        "name": r"\b[A-Z][a-z]* [A-Z][a-z]*\b",
        "location": r"\b[A-Z][a-z]*, [A-Z][a-z]*\b",
        "gmail": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    }

    # Open the input PDF
    doc = fitz.open(input_pdf_path)

    # Iterate through each page
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        print(page)

        page_text = page.get_text("text")
        print(page_text)

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

    # Save the redacted PDF
    doc.save(output_pdf_path)
    doc.close()
    print("Regex redactor function used")


nlp = spacy.load("en_core_web_lg")


def redact_names_from_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    print('Using name redactor')

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        spacy_doc = nlp(text)
        print(text)

        for ent in spacy_doc.ents:
            if ent.label_ == "PERSON":
                name_text = ent.text
                print(name_text)

                regex_pattern = r"\b" + re.escape(name_text) + r"\b"  # Word boundaries
                matches = re.finditer(regex_pattern, text, re.IGNORECASE)

                for match in matches:
                    rects_to_redact = []
                    words = page.get_text("words")

                    for word_info in words:  # Iterate through word *information*
                        word_text = word_info[4]  # The actual word text
                        if name_text.lower() in word_text.lower(): # Case-insensitive comparison
                            rect = fitz.Rect(word_info[:4])  # Coordinates
                            rects_to_redact.append(rect)

                    if rects_to_redact:
                        combined_rect = rects_to_redact[0]
                        for rect in rects_to_redact[1:]:
                            combined_rect |= rect  # Union of rectangles

                        # Padding (improved)
                        padding_x = combined_rect.width * 0.1
                        padding_y = combined_rect.height * 0.1
                        combined_rect.x0 -= padding_x
                        combined_rect.y0 -= padding_y
                        combined_rect.x1 += padding_x
                        combined_rect.y1 += padding_y

                        page.draw_rect(combined_rect, color=(0, 0, 0), fill=(0, 0, 0))

    doc.save(output_pdf)
    doc.close()
    print("Finished redacting names.")







