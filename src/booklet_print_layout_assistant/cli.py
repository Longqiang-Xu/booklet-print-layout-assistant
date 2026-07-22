from __future__ import annotations

import argparse
import sys
from pathlib import Path

from booklet_print_layout_assistant.core.pdf_writer import split_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="booklet-print",
        description=(
            "Prepare booklet print layouts. "
            "The current command splits a reading-order PDF into booklet-sized parts."
        ),
    )
    parser.add_argument("input_pdf", type=Path, help="PDF to split.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--max-sheets",
        type=int,
        default=None,
        help="Maximum sheets per booklet. Defaults to 14.",
    )
    mode.add_argument(
        "--booklet-count",
        type=int,
        default=None,
        help="Split into a fixed number of booklets.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to <input-name>_booklets beside the PDF.",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Output filename prefix. Defaults to the input PDF stem.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = split_pdf(
            args.input_pdf,
            output_dir=args.output_dir,
            max_sheets=args.max_sheets,
            booklet_count=args.booklet_count,
            prefix=args.prefix,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Input pages: {result.page_count}")
    print(f"Generated booklets: {result.booklet_count}")
    print(f"Output directory: {result.output_dir}")
    for booklet in result.booklets:
        plan = booklet.plan
        print(
            f"{plan.index:02d}: pages {plan.start_page}-{plan.end_page}, "
            f"{plan.sheet_count} sheets, {plan.blank_count} blank -> {booklet.path.name}"
        )
    print(f"Manifest: {result.manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
