import fitz


def watermark_pdf(input_pdf_path, output_pdf_path, watermark_text):
    doc = fitz.open(input_pdf_path)

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        font_size = 36
        color = (0.8,0.8,0.8)
        rotate = 45

        page_width, page_height = page.rect.width, page.rect.height


        x_spacing = 150
        y_spacing = 150

        for x in range(0, int(page_width), x_spacing):
            for y in range(0, int(page_height), y_spacing):

                text_position = fitz.Point(x, y)
                page.insert_text(
                    text_position,
                    watermark_text,
                    fontsize=font_size,
                    color=color,
                    rotate=rotate,
                    overlay=True  # Ensures the watermark is added on top
                )


    doc.save(output_pdf_path)
    doc.close()
