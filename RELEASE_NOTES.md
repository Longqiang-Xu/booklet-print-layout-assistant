# Booklet Print Layout Assistant v0.2.0

This release adds page selection before booklet splitting.

## Download

For Windows, download:

```text
BookletPrintLayoutAssistant-v0.2.0-windows-x64.zip
```

Unzip it and run:

```text
BookletPrintLayoutAssistant\BookletPrintLayoutAssistant.exe
```

## Highlights

- Added a page selector in the desktop UI.
- Added page range input such as `1-20,25,-3`.
- Added all/select-none/invert controls for page selection.
- Booklet plans are recalculated from the selected page count.
- Generated PDFs include only selected source pages.
- Added CLI page selection with `booklet-print --pages`.
- Updated README screenshots.

## Notes

- This release still expects the input PDF to already be in reading order.
- Page selection currently shows page numbers, not rendered PDF thumbnails.
- True 2-up A4 booklet imposition is still planned for a future release.

## Verification

Before packaging this release:

- `python -m pytest` passed with 15 tests.
- `python -m compileall src tests` passed.
- `python -m booklet_print_layout_assistant.cli --help` showed `--pages`.
- CLI generation with `--pages "1-3,5"` wrote a 4-page output PDF.
- The page selector UI was visually checked in a browser preview.
