import os
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

# Agordi la tiparon
FONT_PATH = "AlexBrush-Regular.ttf"
pdfmetrics.registerFont(TTFont("AlexBrush", FONT_PATH))

# Dosieroj
BASE_CERTIFICATE = "sxablono_instruistoj.pdf"
STUDENT_LIST = "instruistoj.txt"
OUTPUT_DIR = "Atestiloj"

# Krei la dosierujon se ĝi ne ekzistas
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Legi la lernoliston kaj forigi ".pdf" se ekzistas
with open(STUDENT_LIST, "r", encoding="utf-8") as f:
    students = [line.strip().replace(".pdf", "") for line in f if line.strip()]

def generate_certificate(student_name, output_path):
    # Malfermi la bazan PDF-dosieron
    doc = fitz.open(BASE_CERTIFICATE)
    page = doc[0]  # Supozi ke la atestilo estas en la unua paĝo

    # Krei novan PDF kun la nomo de la studento
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Agordi la tiparon kaj grandecon
    font_size = 48
    can.setFont("AlexBrush", font_size)

    # Akiri la larĝon de la paĝo
    page_width = letter[0]

    # Akiri la larĝon de la teksto por kalkuli la centron
    text_width = can.stringWidth(student_name, "AlexBrush", font_size)
    x_position = (page_width - text_width) / 2  # Centri la tekston

    # Pozicio de la nomo en la atestilo
    y_position = 470

    # Desegni la nomon
    can.drawString(x_position, y_position, student_name)

    # Konservi en memoro
    can.save()
    packet.seek(0)

    # Ŝargi la novan PDF enhavantan la nomon
    overlay = fitz.open("pdf", packet.read())

    # Krei novan paĝon kun la originala enhavo kaj la nova teksto
    new_doc = fitz.open()
    new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
    
    # Aldoni la originalan paĝon
    new_page.show_pdf_page(new_page.rect, doc, 0)

    # Aldoni la tavolon kun la nomo
    new_page.show_pdf_page(new_page.rect, overlay, 0)

    # Konservi la finitan atestilon
    new_doc.save(output_path)
    new_doc.close()
    doc.close()

# Generi atestilojn por ĉiuj studentoj
for student in students:
    output_filename = os.path.join(OUTPUT_DIR, f"KEL_{student}.pdf")
    generate_certificate(student, output_filename)
    print(f"Atestilo generita: {output_filename}")




