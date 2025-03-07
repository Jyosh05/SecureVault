import fitz


def watermark_pdf(input_pdf_path, watermark_text='nobody', output_pdf_path=None):
    try:
        # Open the PDF
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return None

    # If no output path is provided, generate a default output path
    if output_pdf_path is None:
        output_pdf_path = f"{input_pdf_path}_watermarked.pdf"

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        font_size = 36
        color = (0.8, 0.8, 0.8)  # Light gray
        rotate = 270

        page_width, page_height = page.rect.width, page.rect.height

        x_spacing = 150
        y_spacing = 150

        # Iterate over the page dimensions and place the watermark text
        for x in range(0, int(page_width), x_spacing):
            for y in range(0, int(page_height), y_spacing):
                text_position = fitz.Point(x, y)

                # Insert watermark at the given position
                page.insert_text(
                    text_position,
                    watermark_text,
                    fontsize=font_size,
                    color=color,
                    rotate=rotate,
                    overlay=False,
                    render_mode=1
                )

    # Save the watermarked PDF to the specified output path
    try:
        doc.save(output_pdf_path)
        doc.close()
    except Exception as e:
        print(f"Error{e}")

    return output_pdf_path  # Return the path to the saved file
