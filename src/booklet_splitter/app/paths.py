from __future__ import annotations

from importlib import resources
from pathlib import Path


def frontend_index_path() -> Path:
    return Path(resources.files("booklet_splitter").joinpath("frontend", "index.html"))
