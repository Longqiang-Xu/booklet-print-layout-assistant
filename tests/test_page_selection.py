from __future__ import annotations

import pytest

from booklet_print_layout_assistant.core.page_selection import normalize_page_numbers, parse_page_selection


def test_blank_page_selection_means_all_pages() -> None:
    assert parse_page_selection("", total_pages=5) == (1, 2, 3, 4, 5)
    assert parse_page_selection("全部", total_pages=3) == (1, 2, 3)


def test_page_selection_can_include_ranges_and_single_pages() -> None:
    assert parse_page_selection("1-3, 5，7", total_pages=8) == (1, 2, 3, 5, 7)


def test_page_selection_can_remove_from_included_pages() -> None:
    assert parse_page_selection("1-5,-3", total_pages=8) == (1, 2, 4, 5)


def test_page_selection_can_start_in_exclude_mode() -> None:
    assert parse_page_selection("-1-2,5", total_pages=6) == (3, 4, 6)


def test_page_selection_rejects_invalid_or_empty_selections() -> None:
    with pytest.raises(ValueError, match="outside"):
        parse_page_selection("1-6", total_pages=5)
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_page_selection("-1-5", total_pages=5)
    with pytest.raises(ValueError, match="Invalid"):
        parse_page_selection("1,a", total_pages=5)


def test_normalize_page_numbers_sorts_and_deduplicates() -> None:
    assert normalize_page_numbers([3, 1, 3, 2], total_pages=4) == (1, 2, 3)
