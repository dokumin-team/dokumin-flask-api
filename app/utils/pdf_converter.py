from fpdf import FPDF
from io import BytesIO

def create_pdf_from_image(image_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.image(BytesIO(image_data), x=10, y=10, w=190)
    pdf_output = BytesIO()
    pdf.output(pdf_output, 'F')
    pdf_output.seek(0)
    return pdf_output.getvalue()
