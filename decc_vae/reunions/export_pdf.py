"""Export PDF A4 (ReportLab) d'une réunion DECC/VAE."""
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor("#0b2545")
NAVY_LIGHT = colors.HexColor("#1d4e89")
RED = colors.HexColor("#c0392b")
LIGHT = colors.HexColor("#f4f6f8")
WHITE = colors.white


def _register_fonts():
    candidates = [
        Path(settings.BASE_DIR) / "static" / "fonts" / "DejaVuSans.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    bold_candidates = [
        Path(settings.BASE_DIR) / "static" / "fonts" / "DejaVuSans-Bold.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
    ]
    regular = next((p for p in candidates if p.exists()), None)
    bold = next((p for p in bold_candidates if p.exists()), None)
    if regular:
        pdfmetrics.registerFont(TTFont("DejaVu", str(regular)))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(bold or regular)))
        return "DejaVu", "DejaVu-Bold"
    return "Helvetica", "Helvetica-Bold"


def _styles(font, font_bold):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "HeaderTitle",
            fontName=font_bold,
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=NAVY,
        )
    )
    styles.add(
        ParagraphStyle(
            "HeaderSub",
            fontName=font,
            fontSize=8,
            leading=11,
            alignment=TA_CENTER,
            textColor=NAVY_LIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            "Section",
            fontName=font_bold,
            fontSize=10,
            leading=13,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle("Body", fontName=font, fontSize=8, leading=11, alignment=TA_JUSTIFY)
    )
    styles.add(ParagraphStyle("Cell", fontName=font, fontSize=6.5, leading=8.5, alignment=TA_LEFT))
    styles.add(ParagraphStyle("CellBold", fontName=font_bold, fontSize=6.5, leading=8.5))
    styles.add(ParagraphStyle("Small", fontName=font, fontSize=7, leading=9, alignment=TA_CENTER))
    return styles


def _header_footer(canvas, doc, generated_on, font, font_bold):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 1.6 * cm, A4[0], 1.6 * cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont(font_bold, 9)
    canvas.drawCentredString(A4[0] / 2, A4[1] - 0.7 * cm, "RÉPUBLIQUE DU NIGER")
    canvas.setFont(font, 7.5)
    canvas.drawCentredString(
        A4[0] / 2,
        A4[1] - 1.15 * cm,
        "Ministère de l'Enseignement et de la Formation Techniques et Professionnels",
    )
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], 1.1 * cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont(font, 7)
    canvas.drawString(1.5 * cm, 0.45 * cm, f"Généré le {generated_on}")
    canvas.drawRightString(A4[0] - 1.5 * cm, 0.45 * cm, f"Page {doc.page}")
    canvas.restoreState()


def export_reunion_pdf(reunion):
    font, font_bold = _register_fonts()
    styles = _styles(font, font_bold)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.3 * cm,
        rightMargin=1.3 * cm,
        topMargin=2.1 * cm,
        bottomMargin=1.5 * cm,
        title=f"Réunion DECC/VAE {reunion.date}",
    )
    story = []
    story.append(Paragraph("DECC / VAE", styles["HeaderTitle"]))
    story.append(
        Paragraph(
            "Direction des Examens, des Concours, des Certifications et de la VAE",
            styles["HeaderSub"],
        )
    )
    story.append(Paragraph(f"Compte rendu de réunion — {reunion.date:%d/%m/%Y}", styles["HeaderTitle"]))
    story.append(Spacer(1, 8))

    info = [
        [
            Paragraph("<b>Date</b>", styles["Cell"]),
            Paragraph(reunion.date.strftime("%d/%m/%Y"), styles["Cell"]),
            Paragraph("<b>Type</b>", styles["Cell"]),
            Paragraph(reunion.get_type_display(), styles["Cell"]),
        ],
        [
            Paragraph("<b>Heure</b>", styles["Cell"]),
            Paragraph(
                f"{reunion.heure_debut:%H:%M}"
                + (f" – {reunion.heure_fin:%H:%M}" if reunion.heure_fin else ""),
                styles["Cell"],
            ),
            Paragraph("<b>Lieu</b>", styles["Cell"]),
            Paragraph(reunion.lieu or "—", styles["Cell"]),
        ],
        [
            Paragraph("<b>Président</b>", styles["Cell"]),
            Paragraph(reunion.president, styles["Cell"]),
            Paragraph("<b>Rapporteur</b>", styles["Cell"]),
            Paragraph(reunion.rapporteur, styles["Cell"]),
        ],
        [
            Paragraph("<b>Participants</b>", styles["Cell"]),
            Paragraph(str(reunion.nombre_participants), styles["Cell"]),
            Paragraph("<b>Prochaine</b>", styles["Cell"]),
            Paragraph(
                reunion.prochaine_reunion.strftime("%d/%m/%Y") if reunion.prochaine_reunion else "—",
                styles["Cell"],
            ),
        ],
    ]
    t = Table(info, colWidths=[3 * cm, 5.3 * cm, 3 * cm, 5.3 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT),
                ("BACKGROUND", (2, 0), (2, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.4, NAVY),
                ("INNERGRID", (0, 0), (-1, -1), 0.2, NAVY_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t)
    story.append(Paragraph("Participants", styles["Section"]))
    story.append(Paragraph(f"<b>Présents :</b> {reunion.participants_presents or '—'}", styles["Body"]))
    story.append(Paragraph(f"<b>Excusés :</b> {reunion.participants_excuses or '—'}", styles["Body"]))
    story.append(Paragraph(f"<b>Absents :</b> {reunion.participants_absents or '—'}", styles["Body"]))

    story.append(Paragraph("Points de la réunion", styles["Section"]))
    headers = ["N°", "Rub.", "Service", "Sujet", "Décision", "Action", "Resp.", "Délai", "Urg.", "Statut"]
    data = [[Paragraph(f"<b>{h}</b>", styles["CellBold"]) for h in headers]]
    critical_rows = []
    for i, point in enumerate(reunion.points.all(), start=1):
        row = [
            Paragraph(str(point.numero), styles["Cell"]),
            Paragraph(point.get_rubrique_display(), styles["Cell"]),
            Paragraph(point.get_service_display(), styles["Cell"]),
            Paragraph(point.sujet or "", styles["Cell"]),
            Paragraph(point.decision or "", styles["Cell"]),
            Paragraph(point.action or "", styles["Cell"]),
            Paragraph(point.responsable or "", styles["Cell"]),
            Paragraph(point.delai.strftime("%d/%m/%Y") if point.delai else "—", styles["Cell"]),
            Paragraph(str(point.urgence), styles["CellBold"] if point.urgence == 5 else styles["Cell"]),
            Paragraph(point.get_statut_display(), styles["Cell"]),
        ]
        data.append(row)
        if point.urgence == 5:
            critical_rows.append(i)

    widths = [0.8 * cm, 1.3 * cm, 2.1 * cm, 3.2 * cm, 2.6 * cm, 2.6 * cm, 2.0 * cm, 1.6 * cm, 1.0 * cm, 1.5 * cm]
    table = Table(data, colWidths=widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.4, NAVY),
        ("INNERGRID", (0, 0), (-1, -1), 0.2, colors.HexColor("#9aa8b8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    for r in critical_rows:
        style_cmds.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#fdecea")))
        style_cmds.append(("TEXTCOLOR", (8, r), (8, r), RED))
        style_cmds.append(("BACKGROUND", (8, r), (8, r), RED))
        style_cmds.append(("TEXTCOLOR", (8, r), (8, r), WHITE))
    table.setStyle(TableStyle(style_cmds))
    story.append(table)

    story.append(Paragraph("Synthèse", styles["Section"]))
    points = list(reunion.points.all())
    n = len(points)
    n5 = sum(1 for p in points if p.urgence == 5)
    n_fait = sum(1 for p in points if p.statut == "fait")
    synth = (
        f"Cette réunion a examiné {n} point(s), dont {n5} critique(s) (urgence 5). "
        f"{n_fait} point(s) marqué(s) comme fait(s). "
        f"{reunion.objet_prochaine or ''} "
        f"{reunion.observations or ''}"
    )
    story.append(Paragraph(synth.strip() or "—", styles["Body"]))
    story.append(Spacer(1, 18))
    sig = Table(
        [
            [
                Paragraph("<b>Président</b><br/><br/>Nom : ________________<br/>Signature :", styles["Cell"]),
                Paragraph("<b>Rapporteur</b><br/><br/>Nom : ________________<br/>Signature :", styles["Cell"]),
            ]
        ],
        colWidths=[8.3 * cm, 8.3 * cm],
    )
    sig.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (0, 0), 0.4, NAVY),
                ("BOX", (1, 0), (1, 0), 0.4, NAVY),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 28),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(sig)

    generated = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")

    def on_page(canvas, doc):
        _header_footer(canvas, doc, generated, font, font_bold)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buffer.seek(0)
    return buffer
