from __future__ import annotations

from pathlib import Path

from booklet_splitter.core.manifest import build_manifest_text
from booklet_splitter.core.models import BookletPlan, OutputBooklet


def test_manifest_lists_booklet_ranges_and_files() -> None:
    booklets = (
        OutputBooklet(
            plan=BookletPlan(
                index=1,
                start_page=1,
                end_page=10,
                sheet_count=3,
                blank_count=2,
            ),
            path=Path("demo_booklet_01.pdf"),
        ),
    )

    text = build_manifest_text(
        input_pdf=Path("demo.pdf"),
        page_count=10,
        split_mode="fixed booklet count: 1",
        booklets=booklets,
    )

    assert "Total pages: 10" in text
    assert "第1-10页，补2页空白" in text
    assert "demo_booklet_01.pdf" in text
