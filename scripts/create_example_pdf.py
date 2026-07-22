from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas


DEFAULT_OUTPUT = Path("examples") / "sample-17-pages.pdf"


def draw_page(pdf: canvas.Canvas, page_number: int, total_pages: int) -> None:
    width, height = A5
    margin = 36

    pdf.setFillColor(colors.HexColor("#f8fafc"))
    pdf.rect(0, 0, width, height, fill=True, stroke=False)

    pdf.setStrokeColor(colors.HexColor("#cbd5e1"))
    pdf.setLineWidth(1)
    pdf.rect(margin, margin, width - margin * 2, height - margin * 2, fill=False, stroke=True)

    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(margin + 20, height - margin - 56, "Booklet Splitter Sample")

    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.drawString(margin + 20, height - margin - 84, "Reading-order source PDF for testing booklet splits.")

    pdf.setFont("Helvetica-Bold", 72)
    pdf.setFillColor(colors.HexColor("#1769e0"))
    page_text = f"{page_number:02d}"
    text_width = pdf.stringWidth(page_text, "Helvetica-Bold", 72)
    pdf.drawString((width - text_width) / 2, height / 2 - 10, page_text)

    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(colors.HexColor("#64748b"))
    footer = f"Page {page_number} of {total_pages}"
    footer_width = pdf.stringWidth(footer, "Helvetica", 11)
    pdf.drawString((width - footer_width) / 2, margin + 22, footer)

    pdf.showPage()


def create_example_pdf(output_path: Path, page_count: int) -> None:
    if page_count < 1:
        raise ValueError("page_count must be at least 1")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A5, invariant=1)
    pdf.setTitle("Booklet Splitter Sample PDF")
    pdf.setAuthor("Booklet Splitter")

    for page_number in range(1, page_count + 1):
        draw_page(pdf, page_number, page_count)

    pdf.save()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a copyright-safe sample PDF.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output PDF path. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=17,
        help="Number of pages to generate. Default: 17.",
    )
    args = parser.parse_args()

    create_example_pdf(args.output, args.pages)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
