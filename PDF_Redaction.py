import fitz

def pdfredactor(file_path):
    doc = fitz.open(file_path)
    