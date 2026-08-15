"""Export Word (.docx) d'une réunion DECC/VAE."""
from io import BytesIO
from pathlib import Path

from django.conf import settings
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


NAVY = RGBColor(0x0B, 0x25, 0x45)
RED = RGBColor(0xC0, 0x39, 0x2B)


def _set_run_font(run, size=12, bold=False, color=None):
    run.font.name = "Times New Roman"
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        from docx.oxml import OxmlElement

        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rFonts.set(qn("w:hAnsi"), "Times New Roman")
    rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = color


def _add_centered(doc, text, size=12, bold=False, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    _set_run_font(run, size=size, bold=bold, color=color)
    return p


def export_reunion_docx(reunion):
    from django.utils import timezone

    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        logo = Path(settings.BASE_DIR) / "static" / "img" / "logo_decc.png"
        if logo.exists():
            run = hp.add_run()
            run.add_picture(str(logo), width=Cm(1.8))
            hp.add_run("  ")
        r = hp.add_run("DECC / VAE — Ministère de l'EFPT (Niger)")
        _set_run_font(r, size=10, bold=True, color=NAVY)
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fr = fp.add_run(
            f"Document généré le {timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M')}"
        )
        _set_run_font(fr, size=9, color=NAVY)

    _add_centered(doc, "RÉPUBLIQUE DU NIGER", 14, True, NAVY)
    _add_centered(
        doc,
        "Ministère de l'Enseignement et de la Formation Techniques et Professionnels",
        11,
        False,
        NAVY,
    )
    _add_centered(doc, "Direction DECC / VAE", 12, True, NAVY)
    _add_centered(doc, f"Compte rendu de réunion du {reunion.date:%d/%m/%Y}", 13, True, NAVY)

    doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("Informations générales")
    _set_run_font(r, size=13, bold=True, color=NAVY)

    rows = [
        ("Date", reunion.date.strftime("%d/%m/%Y")),
        (
            "Horaire",
            f"{reunion.heure_debut:%H:%M}"
            + (f" – {reunion.heure_fin:%H:%M}" if reunion.heure_fin else ""),
        ),
        ("Lieu", reunion.lieu or "—"),
        ("Type", reunion.get_type_display()),
        ("Président", reunion.president),
        ("Rapporteur", reunion.rapporteur),
        ("Nombre de participants", str(reunion.nombre_participants)),
        (
            "Prochaine réunion",
            reunion.prochaine_reunion.strftime("%d/%m/%Y") if reunion.prochaine_reunion else "—",
        ),
    ]
    # recreate with enough rows
    info = doc.add_table(rows=len(rows), cols=2)
    info.style = "Table Grid"
    for i, (label, value) in enumerate(rows):
        c0, c1 = info.rows[i].cells
        c0.text = ""
        c1.text = ""
        r0 = c0.paragraphs[0].add_run(label)
        r1 = c1.paragraphs[0].add_run(value)
        _set_run_font(r0, 12, True)
        _set_run_font(r1, 12, False)

    p = doc.add_paragraph()
    r = p.add_run("Participants")
    _set_run_font(r, size=13, bold=True, color=NAVY)
    for label, text in (
        ("Présents", reunion.participants_presents),
        ("Excusés", reunion.participants_excuses),
        ("Absents", reunion.participants_absents),
    ):
        para = doc.add_paragraph()
        rl = para.add_run(f"{label} : ")
        _set_run_font(rl, 12, True)
        rv = para.add_run(text or "—")
        _set_run_font(rv, 12, False)

    p = doc.add_paragraph()
    r = p.add_run("Tableau des points")
    _set_run_font(r, size=13, bold=True, color=NAVY)

    headers = [
        "N°",
        "Rubrique",
        "Service",
        "Sujet",
        "Décision",
        "Action",
        "Responsable",
        "Délai",
        "Urgence",
        "Statut",
    ]
    points = list(reunion.points.all())
    table = doc.add_table(rows=1 + len(points), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        _set_run_font(run, 10, True, RGBColor(255, 255, 255))
        cell._tc.get_or_add_tcPr().append(
            parse_xml(r'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:fill="0B2545"/>')
        )
    for idx, point in enumerate(points, start=1):
        values = [
            str(point.numero),
            point.get_rubrique_display(),
            point.get_service_display(),
            point.sujet or "",
            point.decision or "",
            point.action or "",
            point.responsable or "",
            point.delai.strftime("%d/%m/%Y") if point.delai else "—",
            str(point.urgence),
            point.get_statut_display(),
        ]
        for j, val in enumerate(values):
            cell = table.rows[idx].cells[j]
            cell.text = ""
            run = cell.paragraphs[0].add_run(val)
            _set_run_font(run, 9, bold=(point.urgence == 5 and j == 8), color=RED if point.urgence == 5 else None)
            if point.urgence == 5:
                cell._tc.get_or_add_tcPr().append(
                    parse_xml(
                        r'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:fill="FDECEA"/>'
                    )
                )

    p = doc.add_paragraph()
    r = p.add_run("Synthèse")
    _set_run_font(r, size=13, bold=True, color=NAVY)
    n = len(points)
    n5 = sum(1 for x in points if x.urgence == 5)
    n_fait = sum(1 for x in points if x.statut == "fait")
    synth = doc.add_paragraph()
    txt = (
        f"Cette réunion a examiné {n} point(s), dont {n5} critique(s). "
        f"{n_fait} point(s) terminé(s). {reunion.objet_prochaine or ''} {reunion.observations or ''}"
    )
    _set_run_font(synth.add_run(txt.strip() or "—"), 12)

    doc.add_paragraph()
    sig = doc.add_table(rows=2, cols=2)
    sig.style = "Table Grid"
    sig.rows[0].cells[0].text = "Président"
    sig.rows[0].cells[1].text = "Rapporteur"
    sig.rows[1].cells[0].text = f"Nom : {reunion.president}\n\nSignature :\n\n"
    sig.rows[1].cells[1].text = f"Nom : {reunion.rapporteur}\n\nSignature :\n\n"
    for row in sig.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                for run in para.runs:
                    _set_run_font(run, 12)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
