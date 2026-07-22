from __future__ import annotations

import pytest

from booklet_splitter.core.planning import (
    build_plan_options,
    distribute_sheets,
    distribute_sheets_by_count,
    make_plan_by_count,
)


def test_distribute_sheets_balances_after_calculating_booklet_count() -> None:
    assert distribute_sheets(total_pages=160, max_sheets=14) == [14, 13, 13]


def test_distribute_sheets_by_fixed_count_balances_evenly() -> None:
    assert distribute_sheets_by_count(total_pages=168, booklet_count=4) == [11, 11, 10, 10]


def test_make_plan_by_count_pads_the_last_booklet() -> None:
    plans = make_plan_by_count(total_pages=10, booklet_count=2)

    assert plans[0].start_page == 1
    assert plans[0].end_page == 8
    assert plans[0].blank_count == 0
    assert plans[1].start_page == 9
    assert plans[1].end_page == 10
    assert plans[1].blank_count == 2


def test_booklet_count_cannot_exceed_sheet_count() -> None:
    with pytest.raises(ValueError):
        distribute_sheets_by_count(total_pages=8, booklet_count=3)


def test_build_plan_options_marks_recommended_count() -> None:
    options = build_plan_options(total_pages=168, recommended_max_sheets=14)

    recommended = [option for option in options if option.is_recommended]
    assert len(recommended) == 1
    assert recommended[0].booklet_count == 3
