# Bancor Plus Technical Paper

This repository contains the Chinese and English editions of the Bancor Plus technical paper.

Bancor Plus is the name used here for an enhanced reserve-curve design for enterprises and teams in the AI era. It is not an official Bancor protocol version. The papers discuss the model, formulas, settlement boundaries, adaptive reserve funding, auditability, and limitations.

## Papers

- [English edition](Bancor_Plus_Technical_Paper_English.pdf)
- [中文版](Bancor_Plus_技术论文_中文版.pdf)

## Rebuild

Python 3, ReportLab, and TrueType editions of the Noto Sans fonts are required. ReportLab cannot embed the PostScript-outline Noto CJK TTC files commonly installed by Linux distributions.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_papers.py
```

Place `NotoSansSC-Medium.ttf` and `NotoSansSC-Bold.ttf` under `fonts/`, or set these variables to installed TrueType font files before rebuilding:

- `BANCOR_PLUS_FONT_REGULAR`
- `BANCOR_PLUS_FONT_BOLD`
- `BANCOR_PLUS_FONT_MONO`
- `BANCOR_PLUS_FONT_CJK`
- `BANCOR_PLUS_FONT_CJK_BOLD`

The output directory defaults to the repository root. Set `BANCOR_PLUS_OUTPUT_DIR` to override it.

## Scope

The test-data snapshot is illustrative and is not an earnings forecast, valuation opinion, legal advice, or trading recommendation.
