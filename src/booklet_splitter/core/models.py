from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BookletPlan:
    index: int
    start_page: int
    end_page: int
    sheet_count: int
    blank_count: int

    @property
    def content_page_count(self) -> int:
        return self.end_page - self.start_page + 1

    @property
    def output_page_count(self) -> int:
        return self.sheet_count * 4

    def to_dict(self) -> dict[str, int]:
        return {
            "index": self.index,
            "start_page": self.start_page,
            "end_page": self.end_page,
            "sheet_count": self.sheet_count,
            "blank_count": self.blank_count,
            "content_page_count": self.content_page_count,
            "output_page_count": self.output_page_count,
        }


@dataclass(frozen=True)
class PlanOption:
    booklet_count: int
    sheet_counts: tuple[int, ...]
    ranges: tuple[str, ...]
    blank_count: int
    is_recommended: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "booklet_count": self.booklet_count,
            "sheet_counts": list(self.sheet_counts),
            "ranges": list(self.ranges),
            "blank_count": self.blank_count,
            "is_recommended": self.is_recommended,
        }


@dataclass(frozen=True)
class OutputBooklet:
    plan: BookletPlan
    path: Path

    def to_dict(self) -> dict[str, object]:
        data = self.plan.to_dict()
        data["path"] = str(self.path)
        data["file_name"] = self.path.name
        return data


@dataclass(frozen=True)
class SplitResult:
    input_pdf: Path
    output_dir: Path
    page_count: int
    split_mode: str
    booklets: tuple[OutputBooklet, ...]
    manifest_path: Path
    manifest_text_path: Path

    @property
    def booklet_count(self) -> int:
        return len(self.booklets)

    def to_dict(self) -> dict[str, object]:
        return {
            "input_pdf": str(self.input_pdf),
            "output_dir": str(self.output_dir),
            "page_count": self.page_count,
            "split_mode": self.split_mode,
            "booklet_count": self.booklet_count,
            "manifest_path": str(self.manifest_path),
            "manifest_text_path": str(self.manifest_text_path),
            "booklets": [booklet.to_dict() for booklet in self.booklets],
        }
