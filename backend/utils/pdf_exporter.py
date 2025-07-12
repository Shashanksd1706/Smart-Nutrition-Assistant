from fpdf import FPDF
import os

def generate_pdf(text, filename="meal_plan.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Wrap lines that are too long
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)

    path = os.path.join("backend", filename)
    pdf.output(path)
    return path
