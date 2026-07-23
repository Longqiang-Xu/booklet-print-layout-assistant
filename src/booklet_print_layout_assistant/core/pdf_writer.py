from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf._page import PageObject
from pypdf.generic import NameObject

from booklet_print_layout_assistant.core.manifest import write_manifest_files
from booklet_print_layout_assistant.core.models import BookletPlan, OutputBooklet, SplitResult
from booklet_print_layout_assistant.core.page_selection import normalize_page_numbers, parse_page_selection
from booklet_print_layout_assistant.core.planning import make_plan, make_plan_by_count


def read_pdf_page_count(input_pdf: Path) -> int:
    reader = PdfReader(str(input_pdf))
    return len(reader.pages)


def default_output_dir(input_pdf: Path) -> Path:
    return input_pdf.with_name(f"{input_pdf.stem}_booklets")


def clone_blank_like(page: PageObject) -> PageObject:
    media = page.mediabox
    blank = PageObject.create_blank_page(width=float(media.width), height=float(media.height))
    blank.mediabox = page.mediabox
    blank.cropbox = page.cropbox
    if "/Rotate" in page:
        blank[NameObject("/Rotate")] = page["/Rotate"]
    return blank


def page_for_position(
    reader: PdfReader,
    plan: BookletPlan,
    position: int,
    page_numbers: Sequence[int],
) -> PageObject:
    selected_page_index = plan.start_page + position - 1
    if selected_page_index <= plan.end_page:
        source_page_no = page_numbers[selected_page_index - 1]
        return reader.pages[source_page_no - 1]

    blank_source_page_no = page_numbers[plan.end_page - 1]
    return clone_blank_like(reader.pages[blank_source_page_no - 1])


def write_booklet_pdf(
    reader: PdfReader,
    plan: BookletPlan,
    output_path: Path,
    page_numbers: Sequence[int],
) -> None:
    writer = PdfWriter()
    for position in range(1, plan.output_page_count + 1):
        writer.add_page(page_for_position(reader, plan, position, page_numbers))

    with output_path.open("wb") as output_file:
        writer.write(output_file)


def output_name(prefix: str, plan: BookletPlan) -> str:
    return (
        f"{prefix}_booklet_{plan.index:02d}_"
        f"p{plan.start_page:03d}-{plan.end_page:03d}_"
        f"{plan.sheet_count:02d}sheets.pdf"
    )


def split_pdf(
    input_pdf: Path | str,
    *,
    output_dir: Path | str | None = None,
    max_sheets: int | None = None,
    booklet_count: int | None = None,
    prefix: str | None = None,
    page_numbers: Sequence[int] | None = None,
    page_selection: str | None = None,
) -> SplitResult:
    input_path = Path(input_pdf).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"PDF not found: {input_path}")
    if input_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")
    if max_sheets is not None and booklet_count is not None:
        raise ValueError("Use either max_sheets or booklet_count, not both.")
    if page_numbers is not None and page_selection is not None:
        raise ValueError("Use either page_numbers or page_selection, not both.")
    if max_sheets is None and booklet_count is None:
        max_sheets = 14

    reader = PdfReader(str(input_path))
    source_page_count = len(reader.pages)
    if source_page_count < 1:
        raise ValueError("PDF must contain at least one page.")
    if page_selection is not None:
        selected_page_numbers = parse_page_selection(page_selection, source_page_count)
    else:
        selected_page_numbers = normalize_page_numbers(page_numbers, source_page_count)
    page_count = len(selected_page_numbers)

    if booklet_count is not None:
        plans = make_plan_by_count(page_count, booklet_count)
        split_mode = f"fixed booklet count: {booklet_count}"
    else:
        assert max_sheets is not None
        plans = make_plan(page_count, max_sheets)
        split_mode = f"maximum sheets per booklet: {max_sheets}"
    if len(selected_page_numbers) != source_page_count:
        split_mode = f"{split_mode}; selected pages: {len(selected_page_numbers)} of {source_page_count}"

    output_path = Path(output_dir).expanduser().resolve() if output_dir else default_output_dir(input_path)
    output_path.mkdir(parents=True, exist_ok=True)
    file_prefix = prefix or input_path.stem

    booklets: list[OutputBooklet] = []
    for plan in plans:
        booklet_path = output_path / output_name(file_prefix, plan)
        write_booklet_pdf(reader, plan, booklet_path, selected_page_numbers)
        booklets.append(OutputBooklet(plan=plan, path=booklet_path))

    result = SplitResult(
        input_pdf=input_path,
        output_dir=output_path,
        page_count=page_count,
        split_mode=split_mode,
        booklets=tuple(booklets),
        manifest_path=output_path / "打印清单.txt",
        manifest_text_path=output_path / "manifest.txt",
    )
    write_manifest_files(result)
    return result
