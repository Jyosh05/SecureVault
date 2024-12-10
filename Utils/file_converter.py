import os
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from Utils.general_utils import allowed_file

def convert_text_to_pdf(text, output_pdf_path):
    c = canvas.Canvas(output_pdf_path, pagesize=letter)
    width, height = letter
    c.drawString(100, height - 100, text)
    c.save()


def convert_docx_to_pdf(docx_file_path, output_pdf_path):
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', docx_file_path])

def convert_xlsx_to_pdf(excel_file_path, output_pdf_path):
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', excel_file_path])

def convert_pptx_to_pdf(pptx_file_path, output_pdf_path):
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', pptx_file_path])

def convert_file_to_pdf(file_path, output_pdf_path):
    filename, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower().strip('.')

    # Check if the file extension is allowed
    if not allowed_file(file_path):
        raise ValueError(f"Unsupported file type: {file_extension}. Only text-based files are allowed.")

    if file_extension == 'txt':
        with open(file_path, 'r') as file:
            text = file.read()
        convert_text_to_pdf(text, output_pdf_path)

    elif file_extension == 'html':
        convert_html_to_pdf(file_path, output_pdf_path)

    elif file_extension == 'docx':
        convert_docx_to_pdf(file_path, output_pdf_path)

    elif file_extension == 'xlsx':
        convert_xlsx_to_pdf(file_path, output_pdf_path)

    elif file_extension == 'pptx':
        convert_pptx_to_pdf(file_path, output_pdf_path)

    print(f"File converted successfully: {output_pdf_path}")