# pdf_generator.py
# Purpose: PDF document generation utility using ReportLab.
# Responsibilities:
#   - Parse markdown strings into styled ReportLab Flowable lists
#   - Build a styled PDF file in memory and return compiled raw bytes
# DO NOT: Write files directly to disk (always return in-memory BytesIO buffers).
# DO NOT: Import API router dependencies or configuration settings.

import io
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger(__name__)


def generate_report_pdf(title: str, markdown_content: str) -> bytes:
    """
    Generate a styled PDF document in memory from raw markdown.

    Args:
        title: Main header title for the report.
        markdown_content: Advisor report markdown text.

    Returns:
        bytes: Compiled PDF raw byte string.
    """
    logger.info(f"Generating PDF report: {title}")
    buffer = io.BytesIO()

    # Configure page settings
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Premium Color Palette
    primary_color = colors.HexColor("#4f46e5")    # Indigo Accent
    secondary_color = colors.HexColor("#1e1b4b")  # Deep Slate Navy
    text_color = colors.HexColor("#374151")       # Body Charcoal

    # Configure custom Typography styles
    title_style = ParagraphStyle(
        "PDFTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=secondary_color,
        alignment=0,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        "PDFH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "PDFH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=secondary_color,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "PDFBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceBefore=4,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "PDFBullet",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceBefore=2,
        spaceAfter=2
    )

    flowables = []

    # Insert Document Title Header
    flowables.append(Paragraph(title, title_style))
    flowables.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=5, spaceAfter=20))

    # Parse and construct Flowables from Markdown
    lines = markdown_content.split("\n")
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Compile markdown formatting tags into HTML styles
        formatted_line = line_stripped.replace("**", "<b>", 1).replace("**", "</b>", 1)
        # Parse subsequent bold tags recursively
        while "**" in formatted_line:
            formatted_line = formatted_line.replace("**", "<b>", 1).replace("**", "</b>", 1)

        # Parse structural Markdown lines
        if line_stripped.startswith("# "):
            text = formatted_line[2:].replace("<b>", "").replace("</b>", "")
            flowables.append(Paragraph(text, h1_style))
        elif line_stripped.startswith("## "):
            text = formatted_line[3:].replace("<b>", "").replace("</b>", "")
            flowables.append(Paragraph(text, h2_style))
        elif line_stripped.startswith("### "):
            text = formatted_line[4:].replace("<b>", "").replace("</b>", "")
            flowables.append(Paragraph(text, h2_style))
        elif line_stripped.startswith("- ") or line_stripped.startswith("* "):
            text = formatted_line[2:]
            flowables.append(Paragraph(f"&bull; {text}", bullet_style))
        else:
            flowables.append(Paragraph(formatted_line, body_style))

    # Layout footer callback adding page numbers dynamically
    def add_page_number(canvas, doc_template):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor("#9ca3af"))
        footer_text = f"CoFoundr Advisor Report  |  Page {doc_template.page}"
        canvas.drawRightString(letter[0] - 54, 36, footer_text)
        canvas.restoreState()

    # Compile the final document
    doc.build(flowables, onFirstPage=add_page_number, onLaterPages=add_page_number)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
