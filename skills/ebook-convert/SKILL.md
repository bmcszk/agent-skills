---
name: ebook-convert
description: Convert ebooks between formats (EPUB, MOBI, AZW3, PDF, etc.) using Calibre's ebook-convert CLI. Use when the user asks to convert an ebook, e.g. "convert epub to mobi/azw3", "zamień epub na mobi", "konwersja e-booka".
---

# Ebook Conversion

`ebook-convert` from Calibre. Basic usage:

```bash
ebook-convert input.epub output.mobi
```

Output format is inferred from the output file extension. Supported: mobi, azw3, epub, pdf, txt, docx, fb2, and more.

## Format choice matters

- **mobi** — legacy; Amazon stopped accepting it for Send-to-Kindle in 2022, new Kindles don't read it. Only when explicitly requested.
- **azw3** — modern Kindle format, keeps formatting/CSS best. Prefer for Kindle devices.
- **epub** — universal; Kindle (2022+) and Send-to-Kindle accept it directly, no conversion needed.

## Useful options

```bash
# cover for mobi (mobi doesn't embed covers well without this)
ebook-convert in.epub out.mobi --mobi-file-type=both

# nicer azw3 with metadata cover
ebook-convert in.epub out.azw3

# fix TOC during conversion
ebook-convert in.epub out.azw3 --toc-threshold=50
```

## Workflow

1. Locate the input file (find if path not given).
2. Run `ebook-convert <in> <out>`; conversion can take 10–60s — use a generous timeout.
3. Verify the output file exists and has non-zero size.
