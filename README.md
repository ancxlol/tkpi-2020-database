# TKPI 2020 Database (Pages 15-83)

Public multi-format database extracted from **Buku Tabel Komposisi Pangan Indonesia tahun 2020** using **PDF pages 15-83 only**.

This repository exists to make the selected nutrition table section easier to query, audit, and reuse in software.

## Included formats

Under `data/`:
- `tkpi_2020_pages_15_83.csv`
- `tkpi_2020_pages_15_83.json`
- `tkpi_2020_pages_15_83.sqlite`
- `summary.json`
- `raw-pages/page-015.txt` … `page-083.txt` for auditability

## Scope

Only the nutrition table pages were extracted:
- **PDF pages 15-83**

All other pages were intentionally ignored.

## Schema

Table: `foods`

Core fields:
- `code`
- `name`
- `source`
- `category`
- `section`
- `page_pdf`

Nutrition fields per 100 g BDD:
- `air_g`
- `energy_kcal`
- `protein_g`
- `fat_g`
- `carb_g`
- `fiber_g`
- `ash_g`
- `calcium_mg`
- `phosphorus_mg`
- `iron_mg`
- `sodium_mg`
- `potassium_mg`
- `copper_mg`
- `zinc_mg`
- `retinol_mcg`
- `beta_carotene_mcg`
- `carotene_total_mcg`
- `thiamin_mg`
- `riboflavin_mg`
- `niacin_mg`
- `vitamin_c_mg`
- `bdd_percent`

## Record count

The current extraction contains **1,066 food records**.

See `data/summary.json` for category counts and missing-value counts.

## Validation

This repo includes:
- raw page text files extracted directly from the source PDF
- the importer script used to build the dataset
- a validation script and validation report

See:
- `scripts/import_tkpi_2020.py`
- `scripts/validate_tkpi_sample.py`
- `VALIDATION.md`
- `validation_sample.json`

## Quick usage

### CSV
Open `data/tkpi_2020_pages_15_83.csv` in spreadsheets or pandas.

### JSON
Use `data/tkpi_2020_pages_15_83.json` for API ingestion or lightweight apps.

### SQLite
```sql
SELECT code, name, energy_kcal, protein_g, fat_g, carb_g
FROM foods
WHERE name LIKE '%nasi%';
```

### Local search helper
```bash
python scripts/query_tkpi_2020.py nasi
python scripts/query_tkpi_2020.py tempe
```

## Rebuilding the database

The importer expects the original source PDF path as an argument.

To rebuild:
```bash
uv run --with pymupdf python scripts/import_tkpi_2020.py '/path/to/Buku Tabel Komposisi Pangan Indonesia tahun 2020.pdf'
```

To rerun the sample validator:
```bash
uv run --with pymupdf python scripts/validate_tkpi_sample.py '/path/to/Buku Tabel Komposisi Pangan Indonesia tahun 2020.pdf'
```

## Source note

Source document:
- `Buku Tabel Komposisi Pangan Indonesia tahun 2020`

This repository republishes a structured extraction of selected table pages for easier public access. Users should still consult the original publication for official context, methodology, and provenance.

## License note

No additional rights are claimed over the underlying source data. Check the original source publication and publisher terms before downstream commercial redistribution.
