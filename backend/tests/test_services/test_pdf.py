# test_pdf.py
# Purpose: Unit tests for PDF generation utilities.
# Responsibilities:
#   - Compile test markdown content into PDF bytes and assert format signature correctness
# DO NOT: Write files to the server filesystem during tests.

from app.utils.pdf_generator import generate_report_pdf


def test_pdf_generation_bytes():
    """Verify markdown compiler returns valid PDF bytes starting with standard signature."""
    title = "Test Report PDF Layout"
    markdown = (
        "# Executive Summary\n"
        "This is a paragraph test.\n"
        "## Key Details\n"
        "- Bullet item one\n"
        "- Bullet item two\n"
    )

    pdf_bytes = generate_report_pdf(title, markdown)

    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
    # Verify standard PDF magic file header signature (%PDF-)
    assert pdf_bytes.startswith(b"%PDF-")
