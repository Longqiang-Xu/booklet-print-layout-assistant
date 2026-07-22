# Booklet Splitter v0.1.0

This is the first public preview release of Booklet Splitter.

## Download

For Windows, download:

```text
BookletSplitter-v0.1.0-windows-x64.zip
```

Unzip it and run:

```text
BookletSplitter\BookletSplitter.exe
```

## Highlights

- Desktop UI for splitting reading-order PDFs into booklet-sized parts.
- Split by maximum sheets per booklet.
- Split by fixed booklet count.
- Automatic blank-page padding to fill booklet capacity.
- Print manifest output: `打印清单.txt` and `manifest.txt`.
- Command line interface: `booklet-split`.
- Copyright-safe 17-page sample PDF.

## Limitations

- Windows is the primary tested platform.
- This release does not create true 2-up A4 imposition PDFs.
- This release does not manage print queues or call SumatraPDF.
- This release does not detect or split color pages.
- The input PDF should already be in reading order.

## Verification

Before packaging this release:

- `python -m pytest` passed with 8 tests.
- The sample PDF was rendered and visually checked.
- The Windows PyInstaller build completed.
- The packaged `BookletSplitter.exe` started successfully.
