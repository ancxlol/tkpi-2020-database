# Validation report

This report documents pre-publication checks to confirm that the extracted database matches real values from the source PDF.

## Source
- Document: `Buku Tabel Komposisi Pangan Indonesia tahun 2020`
- Scope used: PDF pages `15-83` only

## Validation method

Validation was done in two layers:

1. **Structural checks**
   - record count generated successfully
   - category coverage present across pages 15-83
   - CSV, JSON, and SQLite outputs agree on row count
   - raw page text snapshots exist for every included page

2. **Sample truth checks against the PDF**
   - selected codes across multiple categories were read directly from the source PDF using word-position extraction
   - extracted database values were compared against direct PDF reads for key fields such as name, source, energy, protein, fat, carbs, and sodium where available

## Current result

Validation status: **PASS**

## Sample codes checked
- `AR001` — Beras giling, mentah
- `AP001` — Nasi
- `BP001` — Batatas kelapa, ubi, bakar
- `CP076` — Tempe kedelai murni, goreng
- `DP001` — Bayam, kukus
- `EP001` — Barongko
- `FP001` — Ayam, ampela, goreng
- `GP001` — Bekicot, dendeng, mentah
- `HP001` — Telur ayam, dadar, masakan
- `JP001` — Es krim
- `KP001` — Margarin
- `MP001` — Coklat manis, batang
- `NP001` — Balichong
- `QR001` — Kelapa muda, air, segar

See `validation_sample.json` for exact comparison output.

## Caveats
- Blank values in the source remain blank/NULL in the extracted database.
- This repository does not invent missing values.
- The extraction is designed for correctness and auditability, but the original publication remains the authoritative reference.
