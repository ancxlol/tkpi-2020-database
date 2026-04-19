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

Primary source document used for this repository:
- **Tabel Komposisi Pangan Indonesia (2020)**
- Publisher shown on the cover: **Kementerian Kesehatan**
- Internal evidence reviewed from the PDF front matter:
  - cover page states `TABEL KOMPOSISI PANGAN INDONESIA — KEMENTERIAN KESEHATAN — 2020`
  - the minister foreword (`Sambutan Menteri Kesehatan RI`) and preface identify the work as a Ministry of Health publication updated in 2020

The extraction in this repository uses only **PDF pages 15-83** from that source document.

## Legal note

This repository is based on a **government document**, but this README does **not** claim that the source is openly licensed.

The most relevant legal text I found is **Undang-Undang Nomor 28 Tahun 2014 tentang Hak Cipta**:
- Official page: `https://peraturan.go.id/id/uu-no-28-tahun-2014`
- Official PDF used for legal reading: `https://peraturan.go.id/files/uu28-2014bt.pdf`

Relevant provisions:
- **Pasal 43 huruf b**: publication/distribution/communication/reproduction of anything carried out by or on behalf of the government is *not considered copyright infringement*, **unless** protection is expressly stated by law, by a statement on the work, or at the time of publication.
- **Pasal 44 ayat (1)**: use/reproduction/adaptation with complete source citation for education, research, scientific writing, reporting, criticism, or review is not considered infringement, so long as it does not unreasonably prejudice the copyright holder.

Important caution:
- **Pasal 42** does *not* make this book automatically public domain; that article covers things like statutes, court decisions, state speeches, and similar categories.
- For this repository, **Pasal 43(b)** is the more relevant government-work provision.
- In the PDF pages I reviewed (`1-14`), I did **not** find an explicit copyright notice, open license, or a direct statement forbidding copying. That is helpful, but it is **not the same thing as a formal open-data license**.

## Practical disclaimer

This repository is published for research, auditability, software access, and public reference.

However:
- it should still be treated as a structured extraction of a government publication,
- users should cite the original source clearly,
- and downstream commercial or high-risk redistribution should be reviewed against the original publication and applicable Indonesian law.
