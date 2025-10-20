from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path

def answers_to_rows(answers: dict, prefix: str = "") -> list:
    rows = []
    for k, v in answers.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            rows.append([key, ""])
            rows.extend(answers_to_rows(v, prefix=key + " > "))
        elif isinstance(v, list):
            rows.append([key, ", ".join(map(str, v))])
        else:
            rows.append([key, str(v)])
    return rows

def build_pdf(output_path: str, assessment: dict) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = []

    title = Paragraph("BilgiGEN - Workcube Assessment Raporu", styles["Title"])
    meta = assessment.get("meta", {})
    header = Paragraph(
        f"{assessment['full_name']} - {assessment.get('company','')}<br/>{assessment['email']} - {assessment['phone']}",
        styles["Normal"]
    )
    elems += [title, Spacer(1, 8), header, Spacer(1, 12)]

    data = [["Soru", "Cevap"]]
    data += answers_to_rows(assessment["answers"])
    table = Table(data, colWidths=[260, 260])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#222222")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.gray),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.HexColor("#f7f7f7")])
    ]))
    elems.append(table)
    elems.append(Spacer(1, 12))
    footer = Paragraph(f"Oluşturulma: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Italic"])
    elems.append(footer)

    doc.build(elems)
    return output_path
