from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        extracted = page.extract_text()

        if extracted:
            pages.append({
                "page": page_number,
                "text": extracted
            })

    return pages

