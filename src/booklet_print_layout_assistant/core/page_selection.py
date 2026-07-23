from __future__ import annotations

import re
from collections.abc import Iterable


RANGE_PATTERN = re.compile(r"^(\d+)(?:\s*-\s*(\d+))?$")
ALL_ALIASES = {"*", "all", "全部", "全选"}


def all_pages(total_pages: int) -> tuple[int, ...]:
    if total_pages < 1:
        raise ValueError("PDF must contain at least one page.")
    return tuple(range(1, total_pages + 1))


def normalize_page_numbers(page_numbers: Iterable[int] | None, total_pages: int) -> tuple[int, ...]:
    if page_numbers is None:
        return all_pages(total_pages)
    if total_pages < 1:
        raise ValueError("PDF must contain at least one page.")

    normalized = sorted({int(page_number) for page_number in page_numbers})
    if not normalized:
        raise ValueError("Page selection cannot be empty.")
    for page_number in normalized:
        if page_number < 1 or page_number > total_pages:
            raise ValueError(f"Page {page_number} is outside the PDF page range 1-{total_pages}.")
    return tuple(normalized)


def parse_page_selection(selection: str | None, total_pages: int) -> tuple[int, ...]:
    """Parse a user page selection string into 1-based page numbers."""
    if total_pages < 1:
        raise ValueError("PDF must contain at least one page.")

    text = (selection or "").strip()
    if not text or text.lower() in ALL_ALIASES:
        return all_pages(total_pages)

    parts = [part.strip() for part in text.replace("，", ",").replace("、", ",").split(",")]
    parts = [part for part in parts if part]
    if not parts:
        return all_pages(total_pages)

    exclude_mode = parts[0].startswith("-")
    selected_pages: set[int] = set(range(1, total_pages + 1)) if exclude_mode else set()

    for part in parts:
        is_removal = exclude_mode or part.startswith("-")
        if part.startswith("-"):
            part = part[1:].strip()
        if not part:
            raise ValueError("Page selection contains an empty removal segment.")

        start_page, end_page = _parse_range_part(part, total_pages)
        pages = range(start_page, end_page + 1)
        if is_removal:
            selected_pages.difference_update(pages)
        else:
            selected_pages.update(pages)

    if not selected_pages:
        raise ValueError("Page selection cannot be empty.")
    return tuple(sorted(selected_pages))


def _parse_range_part(part: str, total_pages: int) -> tuple[int, int]:
    match = RANGE_PATTERN.match(part)
    if match is None:
        raise ValueError(f"Invalid page selection segment: {part}")

    start_page = int(match.group(1))
    end_page = int(match.group(2) or start_page)
    if start_page < 1 or end_page < 1:
        raise ValueError("Page numbers must be at least 1.")
    if start_page > end_page:
        raise ValueError(f"Page range must start before it ends: {part}")
    if end_page > total_pages:
        raise ValueError(f"Page {end_page} is outside the PDF page range 1-{total_pages}.")
    return start_page, end_page
