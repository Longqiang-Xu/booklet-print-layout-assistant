# Contributing

Thanks for helping improve Booklet Print Layout Assistant.

## Development Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

## Guidelines

- Keep the core splitting logic independent from the desktop UI.
- Prefer small, focused changes.
- Add or update tests when changing splitting rules or PDF output behavior.
- Do not add copyrighted sample PDFs or personal print files to the repository.
- Keep generated files such as `dist/`, `build/`, `.venv-build/`, and
  `*_booklets/` out of commits.

## Build

```powershell
.\scripts\build_windows.ps1
```

The packaged app will be written to `dist\BookletPrintLayoutAssistant\`.
