from __future__ import annotations

import base64
import io
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium


@dataclass(frozen=True)
class PageThumbnail:
    page_number: int
    width: int
    height: int
    data_url: str

    def to_dict(self) -> dict[str, int | str]:
        return {
            "page_number": self.page_number,
            "width": self.width,
            "height": self.height,
            "data_url": self.data_url,
        }


def render_page_thumbnails(
    input_pdf: Path | str,
    page_numbers: Iterable[int],
    *,
    target_width: int = 180,
) -> tuple[PageThumbnail, ...]:
    input_path = Path(input_pdf).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"PDF not found: {input_path}")
    if input_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")

    width = min(320, max(90, int(target_width)))
    document = pdfium.PdfDocument(str(input_path))
    try:
        page_count = len(document)
        thumbnails: list[PageThumbnail] = []
        for page_number in page_numbers:
            page_no = int(page_number)
            if page_no < 1 or page_no > page_count:
                raise ValueError(f"Page {page_no} is outside the PDF page range 1-{page_count}.")
            thumbnails.append(_render_thumbnail(document, page_no, width))
        return tuple(thumbnails)
    finally:
        document.close()


def _render_thumbnail(document: pdfium.PdfDocument, page_number: int, target_width: int) -> PageThumbnail:
    page = document[page_number - 1]
    bitmap = None
    try:
        page_width = page.get_width()
        scale = target_width / page_width if page_width else 1
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        data = base64.b64encode(buffer.getvalue()).decode("ascii")
        return PageThumbnail(
            page_number=page_number,
            width=image.width,
            height=image.height,
            data_url=f"data:image/png;base64,{data}",
        )
    finally:
        if bitmap is not None:
            bitmap.close()
        page.close()
