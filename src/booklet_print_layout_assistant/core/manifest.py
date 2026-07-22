from __future__ import annotations

from pathlib import Path

from booklet_print_layout_assistant.core.models import OutputBooklet, SplitResult
from booklet_print_layout_assistant.core.planning import format_page_range_zh


def build_manifest_text(
    *,
    input_pdf: Path,
    page_count: int,
    split_mode: str,
    booklets: tuple[OutputBooklet, ...],
) -> str:
    lines = [
        f"Input PDF: {input_pdf}",
        f"Total pages: {page_count}",
        f"Split mode: {split_mode}",
        "",
        "Generated booklets:",
    ]

    for booklet in booklets:
        plan = booklet.plan
        lines.append(
            f"{plan.index:02d}. {format_page_range_zh(plan)} | "
            f"{plan.sheet_count} sheets | {plan.output_page_count} output pages | "
            f"{booklet.path.name}"
        )

    return "\n".join(lines) + "\n"


def write_manifest_files(result: SplitResult) -> None:
    manifest_text = build_manifest_text(
        input_pdf=result.input_pdf,
        page_count=result.page_count,
        split_mode=result.split_mode,
        booklets=result.booklets,
    )
    result.manifest_path.write_text(manifest_text, encoding="utf-8")
    result.manifest_text_path.write_text(manifest_text, encoding="utf-8")
