from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):

    pdf_reader = PdfReader(pdf_path)

    text = ""

    for page in pdf_reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text