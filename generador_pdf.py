
import os
import qrcode

from reportlab.lib.pagesizes import A6
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


# Carpeta donde se guardarán los boletos
CARPETA_BOLETOS = "boletos"

os.makedirs(CARPETA_BOLETOS, exist_ok=True)


def generar_boleto_pdf(folio, nombre, correo, telefono, numero, total):

    # Crear el código QR con los datos del boleto
    contenido_qr = (
        f"AUDITORIO PLATA\n"
        f"Folio: {folio}\n"
        f"Solicitante: {nombre}\n"
        f"Correo: {correo}\n"
        f"Telefono: {telefono}\n"
        f"Boleto: {numero} de {total}"
    )

    codigo = qrcode.make(contenido_qr)

    # Guardar temporalmente el QR
    ruta_qr = os.path.join(CARPETA_BOLETOS, f"{folio}.png")
    codigo.save(ruta_qr)

    # Crear el PDF
    ruta_pdf = os.path.join(CARPETA_BOLETOS, f"{folio}.pdf")

    pdf = canvas.Canvas(ruta_pdf, pagesize=A6)
    ancho, alto = A6

    # Fondo y borde
    pdf.setFillColor(colors.HexColor("#102B24"))
    pdf.rect(0, 0, ancho, alto, fill=1, stroke=0)

    pdf.setStrokeColor(colors.HexColor("#D4AF37"))
    pdf.setLineWidth(2)
    pdf.roundRect(
        5 * mm, 5 * mm,
        ancho - 10 * mm, alto - 10 * mm,
        4 * mm, fill=0, stroke=1
    )

    # Encabezado
    pdf.setFillColor(colors.HexColor("#F5D76E"))
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawCentredString(ancho / 2, alto - 18 * mm, "AUDITORIO PLATA")

    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(colors.white)
    pdf.drawCentredString(
        ancho / 2, alto - 27 * mm,
        "CONCIERTO NAVIDENO"
    )

    # Datos del boleto
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(12 * mm, alto - 42 * mm, "BOLETO DE ACCESO")

    pdf.setFont("Helvetica", 8)
    pdf.drawString(12 * mm, alto - 52 * mm, f"Nombre: {nombre[:32]}")
    pdf.drawString(12 * mm, alto - 60 * mm, f"Correo: {correo[:35]}")
    pdf.drawString(12 * mm, alto - 68 * mm, f"Telefono: {telefono}")

    pdf.setFillColor(colors.HexColor("#F5D76E"))
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(12 * mm, alto - 80 * mm, f"Folio: {folio}")

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(
        12 * mm, alto - 88 * mm,
        f"Boleto {numero} de {total}"
    )

    # Código QR
    pdf.drawImage(
        ruta_qr,
        ancho - 42 * mm,
        10 * mm,
        width=30 * mm,
        height=30 * mm
    )

    pdf.setFont("Helvetica", 7)
    pdf.drawString(12 * mm, 12 * mm, "Presenta este boleto al ingresar.")

    pdf.save()

    return ruta_pdf
