from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import webview

from booklet_splitter.core.pdf_writer import default_output_dir, read_pdf_page_count, split_pdf
from booklet_splitter.core.planning import build_plan_options, total_sheet_count


def ok(data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok": True, "data": data or {}}


def fail(message: str) -> dict[str, Any]:
    return {"ok": False, "error": message}


class AppApi:
    def __init__(self) -> None:
        self._window: webview.Window | None = None

    def set_window(self, window: webview.Window) -> None:
        self._window = window

    def select_pdf(self) -> dict[str, Any]:
        if self._window is None:
            return fail("Window is not ready.")

        paths = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=("PDF files (*.pdf)", "All files (*.*)"),
        )
        selected = self._first_path(paths)
        if selected is None:
            return ok({"cancelled": True})

        return self.analyze_pdf(selected)

    def select_output_dir(self, default_dir: str | None = None) -> dict[str, Any]:
        if self._window is None:
            return fail("Window is not ready.")

        directory = default_dir or str(Path.home())
        paths = self._window.create_file_dialog(
            webview.FOLDER_DIALOG,
            directory=directory,
            allow_multiple=False,
        )
        selected = self._first_path(paths)
        if selected is None:
            return ok({"cancelled": True})

        return ok({"path": str(Path(selected).resolve())})

    def analyze_pdf(self, pdf_path: str) -> dict[str, Any]:
        try:
            input_path = Path(pdf_path).expanduser().resolve()
            page_count = read_pdf_page_count(input_path)
            total_sheets = total_sheet_count(page_count)
            options = build_plan_options(page_count)
            return ok(
                {
                    "pdf_path": str(input_path),
                    "pdf_name": input_path.name,
                    "page_count": page_count,
                    "total_sheets": total_sheets,
                    "default_output_dir": str(default_output_dir(input_path)),
                    "plan_options": [option.to_dict() for option in options],
                }
            )
        except Exception as exc:
            return fail(str(exc))

    def get_plan_options(
        self,
        pdf_path: str,
        recommended_max_sheets: int = 14,
        min_sheets_per_booklet: int = 10,
        max_sheets_per_booklet: int = 17,
    ) -> dict[str, Any]:
        try:
            page_count = read_pdf_page_count(Path(pdf_path).expanduser().resolve())
            options = build_plan_options(
                page_count,
                recommended_max_sheets=recommended_max_sheets,
                min_sheets_per_booklet=min_sheets_per_booklet,
                max_sheets_per_booklet=max_sheets_per_booklet,
            )
            return ok({"plan_options": [option.to_dict() for option in options]})
        except Exception as exc:
            return fail(str(exc))

    def split_pdf(self, options: dict[str, Any]) -> dict[str, Any]:
        try:
            input_pdf = str(options.get("input_pdf") or "")
            output_dir = str(options.get("output_dir") or "")
            mode = str(options.get("mode") or "max_sheets")
            prefix = options.get("prefix")

            if mode == "fixed_count":
                result = split_pdf(
                    input_pdf,
                    output_dir=output_dir or None,
                    booklet_count=int(options.get("booklet_count") or 1),
                    prefix=str(prefix) if prefix else None,
                )
            else:
                result = split_pdf(
                    input_pdf,
                    output_dir=output_dir or None,
                    max_sheets=int(options.get("max_sheets") or 14),
                    prefix=str(prefix) if prefix else None,
                )
            return ok(result.to_dict())
        except Exception as exc:
            return fail(str(exc))

    def open_output_folder(self, path: str) -> dict[str, Any]:
        try:
            folder = Path(path).expanduser().resolve()
            if not folder.exists():
                return fail(f"Folder does not exist: {folder}")
            if os.name == "nt":
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
            return ok()
        except Exception as exc:
            return fail(str(exc))

    @staticmethod
    def _first_path(paths: object) -> str | None:
        if paths is None:
            return None
        if isinstance(paths, (list, tuple)):
            return str(paths[0]) if paths else None
        return str(paths)
