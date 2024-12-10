import fitz  # PyMuPDF
import re


def redact_pdf(input_pdf_path, output_pdf_path):
    """Redact personal information in a PDF using black rectangles."""
    # Define regex patterns for personal information
    patterns = {
        "credit_card": r"\b(?:\d[ -]*?){13,16}\b",  # Match credit card numbers
        "nric": r"\b[A-Z]\d{7}[A-Z]\b",  # Match Singapore NRIC numbers
        "name": r"\b[A-Z][a-z]* [A-Z][a-z]*\b",  # Example: Firstname Lastname (basic)
        "location": r"\b[A-Z][a-z]*, [A-Z][a-z]*\b",  # Example: Location like 'New York'
    }

    # Open the input PDF
    doc = fitz.open(input_pdf_path)

    # Iterate through each page
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Load a page

        # Extract the text and find positions of matches
        page_text = page.get_text("text")

        for label, pattern in patterns.items():
            # Use regex to find all occurrences of the sensitive data
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