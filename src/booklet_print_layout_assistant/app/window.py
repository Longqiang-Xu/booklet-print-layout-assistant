from __future__ import annotations

import os

from booklet_print_layout_assistant.app.api import AppApi
from booklet_print_layout_assistant.app.paths import frontend_index_path


def main() -> int:
    try:
        import webview
    except ImportError as exc:
        raise SystemExit("pywebview is not installed. Run: python -m pip install pywebview") from exc

    api = AppApi()
    window = webview.create_window(
        "Booklet Print Layout Assistant",
        frontend_index_path().as_uri(),
        js_api=api,
        width=980,
        height=720,
        min_size=(760, 560),
    )
    api.set_window(window)
    webview.start(debug=os.environ.get("BOOKLET_PRINT_LAYOUT_ASSISTANT_DEBUG") == "1")
    return 0
