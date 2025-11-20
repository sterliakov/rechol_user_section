from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONTS_ROOT = Path(__file__).parent / "fonts"
CERTIFICATES_ROOT = Path(__file__).parent / "files" / "certificates"


def add_fonts():
    for metric in ["Regular", "Bold", "Italic", "BoldItalic"]:
        pdfmetrics.registerFont(
            TTFont(
                f"LiberationSans-{metric}",
                str(FONTS_ROOT / f"Liberation_Sans/LiberationSans-{metric}.ttf"),
            ),
        )


add_fonts()


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
        can.setFont("LiberationSans-Italic", 56)
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


def make_organizer_thanks_cert(cert):
    src = CERTIFICATES_ROOT / "organizer_thanks.pdf"
    max_venue_length_big_font = 20

    with src.open("rb") as src:
        existing_pdf = PdfReader(src)
        page = existing_pdf.pages[0]

        packet = io.BytesIO()
        can = canvas.Canvas(
            packet,
            pagesize=(page.mediabox.width, page.mediabox.height),
        )
        can.setFont("LiberationSans-Italic", 48)
        can.setFillColorRGB(0x12 / 0xFF, 0x02 / 0xFF, 0x49 / 0xFF)
        can.drawCentredString(800, 595, cert.last_name_gen)
        can.drawCentredString(
            800,
            530,
            " ".join(filter(None, [cert.first_name_gen, cert.middle_name_gen])),
        )
        venue = cert.venue.short_name
        can.setFont(
            "LiberationSans-Italic",
            24 if len(venue) > max_venue_length_big_font else 36,
        )
        can.drawCentredString(800, 475, f"(площадка {venue})")
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
