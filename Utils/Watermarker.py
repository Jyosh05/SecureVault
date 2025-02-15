import fitz


def watermark_pdf(input_pdf_path, watermark_text='nobody', output_pdf_path=None):
    try:
        # Open the PDF
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return None

    print(f"Watermark Text: {watermark_text}")

    # If no output path is provided, generate a default output path
    if output_pdf_path is None:
        output_pdf_path = f"{input_pdf_path}_watermarked.pdf"

    for page_num in range(doc.page_count):
        print(f"Processing page {page_num + 1}...")  # Print which page is being processed
        page = doc.load_page(page_num)

        font_size = 36
        color = (0.8, 0.8, 0.8)  # Light gray
        rotate = 270

        page_width, page_height = page.rect.width, page.rect.height
        print(f"Page size: {page_width}x{page_height}")

        x_spacing = 150
        y_spacing = 150

        # Iterate over the page dimensions and place the watermark text
        for x in range(0, int(page_width), x_spacing):
            for y in range(0, int(page_height), y_spacing):
                text_position = fitz.Point(x, y)
                print(f"Inserting watermark at position ({x}, {y})")

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
        print(f"Watermarked PDF saved to {output_pdf_path}")
    except Exception as e:
        print(f"Error saving watermarked PDF: {e}")
        return None

    return output_pdf_path  # Return the path to the saved file
