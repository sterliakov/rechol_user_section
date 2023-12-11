from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

CERTIFICATES_ROOT = Path(__file__).parent / "files" / "certificates"


def make_prelim_offline_cert(user):
    src = CERTIFICATES_ROOT / f"prelim_offline_{user.participation_form}.pdf"
    with src.open("rb") as src:
        existing_pdf = PdfReader(src)
        page = existing_pdf.pages[0]

        packet = io.BytesIO()
        can = canvas.Canvas(
            packet,
            pagesize=(page.mediabox.width, page.mediabox.height),
        )
        can.setFont("Helvetica", 56)
        can.setFillColorRGB(0x12 / 0xFF, 0x02 / 0xFF, 0x49 / 0xFF)
        can.drawString(560, 630, user.first_name)
        can.drawString(560, 550, user.last_name)
        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        page.merge_page(new_pdf.pages[0])

        output = PdfWriter()
        output.add_page(page)
        dest = io.BytesIO()
        output.write(dest)

    dest.seek(0)
    return dest
