from __future__ import annotations

import math

from booklet_print_layout_assistant.core.models import BookletPlan, PlanOption


def total_sheet_count(total_pages: int) -> int:
    if total_pages < 1:
        raise ValueError("PDF must contain at least one page.")
    return math.ceil(total_pages / 4)


def distribute_sheets(total_pages: int, max_sheets: int) -> list[int]:
    if max_sheets < 1:
        raise ValueError("max_sheets must be at least 1.")

    total_sheets = total_sheet_count(total_pages)
    booklet_count = math.ceil(total_sheets / max_sheets)
    base = total_sheets // booklet_count
    extra = total_sheets % booklet_count

    return [base + 1 if index < extra else base for index in range(booklet_count)]


def distribute_sheets_by_count(total_pages: int, booklet_count: int) -> list[int]:
    if booklet_count < 1:
        raise ValueError("booklet_count must be at least 1.")

    total_sheets = total_sheet_count(total_pages)
    if booklet_count > total_sheets:
        raise ValueError(f"booklet_count cannot exceed total sheet count ({total_sheets}).")

    base = total_sheets // booklet_count
    extra = total_sheets % booklet_count

    return [base + 1 if index < extra else base for index in range(booklet_count)]


def make_plan_from_sheet_counts(total_pages: int, sheet_counts: list[int]) -> list[BookletPlan]:
    total_sheet_count(total_pages)
    if not sheet_counts:
        raise ValueError("sheet_counts cannot be empty.")
    if any(sheet_count < 1 for sheet_count in sheet_counts):
        raise ValueError("each booklet must contain at least one sheet.")

    plans: list[BookletPlan] = []
    next_page = 1

    for index, sheet_count in enumerate(sheet_counts, start=1):
        capacity = sheet_count * 4
        remaining = total_pages - next_page + 1
        content_count = min(capacity, remaining)
        start_page = next_page
        end_page = start_page + content_count - 1
        blank_count = capacity - content_count

        plans.append(
            BookletPlan(
                index=index,
                start_page=start_page,
                end_page=end_page,
                sheet_count=sheet_count,
                blank_count=blank_count,
            )
        )
        next_page = end_page + 1

    if next_page <= total_pages:
        raise ValueError("sheet_counts do not provide enough capacity for all pages.")

    return plans


def make_plan(total_pages: int, max_sheets: int) -> list[BookletPlan]:
    return make_plan_from_sheet_counts(total_pages, distribute_sheets(total_pages, max_sheets))


def make_plan_by_count(total_pages: int, booklet_count: int) -> list[BookletPlan]:
    return make_plan_from_sheet_counts(
        total_pages,
        distribute_sheets_by_count(total_pages, booklet_count),
    )


def format_page_range(plan: BookletPlan) -> str:
    if plan.blank_count:
        return f"{plan.start_page}-{plan.end_page} (+{plan.blank_count} blank)"
    return f"{plan.start_page}-{plan.end_page}"


def format_page_range_zh(plan: BookletPlan) -> str:
    if plan.blank_count:
        return f"第{plan.start_page}-{plan.end_page}页，补{plan.blank_count}页空白"
    return f"第{plan.start_page}-{plan.end_page}页"


def sheet_range_violation(plans: list[BookletPlan], min_sheets: int, max_sheets: int) -> int:
    return sum(
        max(0, min_sheets - plan.sheet_count) + max(0, plan.sheet_count - max_sheets)
        for plan in plans
    )


def suitable_booklet_counts(
    total_pages: int,
    min_count: int,
    max_count: int,
    min_sheets: int,
    max_sheets: int,
    recommended_count: int,
) -> list[int]:
    total_sheets = total_sheet_count(total_pages)
    max_count = min(max_count, total_sheets)
    if min_count > max_count:
        min_count = max_count

    all_counts = list(range(min_count, max_count + 1))
    suitable = [
        booklet_count
        for booklet_count in all_counts
        if sheet_range_violation(
            make_plan_by_count(total_pages, booklet_count),
            min_sheets,
            max_sheets,
        )
        == 0
    ]
    if suitable:
        return suitable

    ranked = sorted(
        all_counts,
        key=lambda booklet_count: (
            sheet_range_violation(
                make_plan_by_count(total_pages, booklet_count),
                min_sheets,
                max_sheets,
            ),
            abs(booklet_count - recommended_count),
            booklet_count,
        ),
    )
    return ranked[: min(5, len(ranked))]


def build_plan_options(
    total_pages: int,
    recommended_max_sheets: int = 14,
    min_sheets_per_booklet: int = 10,
    max_sheets_per_booklet: int = 17,
    min_booklets: int = 1,
    max_booklets: int | None = None,
) -> list[PlanOption]:
    total_sheets = total_sheet_count(total_pages)
    recommended_count = len(make_plan(total_pages, recommended_max_sheets))
    effective_max = max_booklets or total_sheets
    counts = suitable_booklet_counts(
        total_pages=total_pages,
        min_count=min_booklets,
        max_count=effective_max,
        min_sheets=min_sheets_per_booklet,
        max_sheets=max_sheets_per_booklet,
        recommended_count=recommended_count,
    )

    options: list[PlanOption] = []
    for count in counts:
        plans = make_plan_by_count(total_pages, count)
        options.append(
            PlanOption(
                booklet_count=count,
                sheet_counts=tuple(plan.sheet_count for plan in plans),
                ranges=tuple(format_page_range_zh(plan) for plan in plans),
                blank_count=sum(plan.blank_count for plan in plans),
                is_recommended=count == recommended_count,
            )
        )
    return options
