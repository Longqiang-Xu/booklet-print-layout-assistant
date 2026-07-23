from __future__ import annotations

from pypdf import PdfWriter

from booklet_print_layout_assistant.core.thumbnails import render_page_thumbnails


def test_render_page_thumbnails_returns_png_data_urls(tmp_path) -> None:
    input_pdf = tmp_path / "thumbs.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=300)
    writer.add_blank_page(width=300, height=200)
    with input_pdf.open("wb") as output_file:
        writer.write(output_file)

    thumbnails = render_page_thumbnails(input_pdf, [1, 2], target_width=100)

    assert [thumbnail.page_number for thumbnail in thumbnails] == [1, 2]
    assert thumbnails[0].width == 100
    assert thumbnails[0].height > 100
    assert thumbnails[1].width == 100
    assert thumbnails[1].height < 100
    assert thumbnails[0].data_url.startswith("data:image/png;base64,")
