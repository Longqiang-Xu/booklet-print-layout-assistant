from __future__ import annotations

from pypdf import PdfReader, PdfWriter

from booklet_print_layout_assistant.core.pdf_writer import split_pdf


def test_split_pdf_writes_padded_booklet_outputs(tmp_path) -> None:
    input_pdf = tmp_path / "input.pdf"
    writer = PdfWriter()
    for _ in range(10):
        writer.add_blank_page(width=200, height=300)
    with input_pdf.open("wb") as output_file:
        writer.write(output_file)

    result = split_pdf(input_pdf, booklet_count=2)
    output_page_counts = [len(PdfReader(str(booklet.path)).pages) for booklet in result.booklets]

    assert result.booklet_count == 2
    assert output_page_counts == [8, 4]
    assert result.booklets[1].plan.blank_count == 2
    assert result.manifest_path.exists()


def test_split_pdf_can_pad_rotated_pages(tmp_path) -> None:
    input_pdf = tmp_path / "rotated.pdf"
    writer = PdfWriter()
    for index in range(5):
        page = writer.add_blank_page(width=200, height=300)
        if index == 4:
            page.rotate(90)
    with input_pdf.open("wb") as output_file:
        writer.write(output_file)

    result = split_pdf(input_pdf, booklet_count=2)

    assert result.booklets[1].plan.blank_count == 3
    assert len(PdfReader(str(result.booklets[1].path)).pages) == 4
