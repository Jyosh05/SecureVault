import fitz  # PyMuPDF
import os
from PIL import Image
import io
from Utils.general_utils import temp_file_sharing_upload


def pdf_to_images(pdf_path):
    """Converts a PDF to a list of image objects"""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Load the page
        pix = page.get_pixmap()  # Render the page as an image
        img_bytes = pix.tobytes("png")  # Convert to bytes (can be other formats like jpeg)
        img = Image.open(io.BytesIO(img_bytes))  # Open image with PIL
        images.append(img)
    return images


def images_to_pdf(pdf_file_name, images, output_pdf_path):
    """Converts a list of images to a single PDF file"""

    upload_folder = temp_file_sharing_upload()  # Get the upload folder

    image_list = []
    for i, img in enumerate(images):
        # Generate a unique image filename using the PDF name and page number
        img_filename = f"{pdf_file_name}_page_{i + 1}.png"
        img_path = os.path.join(upload_folder, img_filename)  # Save using PDF name and page number
        img.save(img_path)
        image_list.append(img_path)

    # Open the first image and save all images into a single PDF
    first_image = Image.open(image_list[0])
    first_image.save(output_pdf_path, save_all=True, append_images=[Image.open(img) for img in image_list[1:]])

    # Optionally, clean up the images after PDF creation (to avoid clutter)
    for img_path in image_list:
        os.remove(img_path)

    print(f"PDF saved at {output_pdf_path}")


def convert_pdf_to_image_pdf(pdf_path, output_directory):
    """Converts the PDF to an image-based PDF and saves with the original filename"""
    # Extract the filename without extension
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

    # Create the output file path using the original filename
    output_pdf_path = os.path.join(output_directory, f"{base_filename}_converted.pdf")

    # Convert PDF pages to images
    images = pdf_to_images(pdf_path)

    # Convert images back to PDF and save it
    images_to_pdf(base_filename, images, output_pdf_path)

    return output_pdf_path
