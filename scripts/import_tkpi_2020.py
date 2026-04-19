#!/usr/bin/env python3
import csv
import json
import re
import sqlite3
import sys
from pathlib import Path

import pymupdf

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PDF = 'Buku Tabel Komposisi Pangan Indonesia tahun 2020.pdf'
PDF_PATH = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path(DEFAULT_PDF)
OUT_DIR = ROOT_DIR / 'data'
RAW_DIR = OUT_DIR / 'raw-pages'

START_PAGE = 15  # 1-indexed, inclusive
END_PAGE = 83    # 1-indexed, inclusive

CODE_RE = re.compile(r'^[A-Z]{2}\d{3}$')
CATEGORY_RE = re.compile(r'^(4\.\d+\.\s+.+)$')
SECTION_MARKERS = {
    'TUNGGAL/SINGLE': 'single',
    'OLAHAN/PRODUK/KOMPOSIT': 'composite',
}

COLUMN_SPECS = [
    ('air_g', 196.9),
    ('energy_kcal', 223.5),
    ('protein_g', 250.5),
    ('fat_g', 275.7),
    ('carb_g', 298.9),
    ('fiber_g', 326.1),
    ('ash_g', 353.1),
    ('calcium_mg', 380.3),
    ('phosphorus_mg', 407.6),
    ('iron_mg', 435.8),
    ('sodium_mg', 463.5),
    ('potassium_mg', 491.1),
    ('copper_mg', 526.6),
    ('zinc_mg', 560.9),
    ('retinol_mcg', 592.9),
    ('beta_carotene_mcg', 623.8),
    ('carotene_total_mcg', 655.0),
    ('thiamin_mg', 679.4),
    ('riboflavin_mg', 707.6),
    ('niacin_mg', 737.8),
    ('vitamin_c_mg', 767.8),
    ('bdd_percent', 791.6),
]

FIELDNAMES = [
    'code', 'name', 'source', 'category', 'section', 'page_pdf',
    *[name for name, _ in COLUMN_SPECS],
]


def norm_space(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def clean_source(text: str) -> str:
    s = norm_space(text)
    s = re.sub(r'\s*-\s*', '-', s)
    return s


def line_groups(words, x_min, x_max, y_min, y_max):
    selected = []
    for w in words:
        x0, y0, x1, y1, text, *_ = w
        if x0 >= x_min and x0 < x_max and y0 >= y_min and y0 < y_max:
            selected.append((x0, y0, text))
    buckets = {}
    for x0, y0, text in selected:
        key = round(y0 / 2) * 2
        buckets.setdefault(key, []).append((x0, text))
    lines = []
    for key in sorted(buckets):
        parts = [t for _, t in sorted(buckets[key], key=lambda z: z[0])]
        line = norm_space(' '.join(parts))
        if line:
            lines.append(line)
    return lines


def parse_number(text: str):
    text = text.strip()
    if not text:
        return None
    text = text.replace(',', '.')
    try:
        if '.' in text:
            return float(text)
        return int(text)
    except ValueError:
        return None


def detect_page_category(page_text: str, fallback: str | None) -> str | None:
    for raw in page_text.splitlines():
        line = norm_space(raw)
        m = CATEGORY_RE.match(line)
        if m:
            return m.group(1)
    return fallback


def detect_section(page_text: str, fallback: str | None) -> str | None:
    for raw in page_text.splitlines():
        line = norm_space(raw)
        if line in SECTION_MARKERS:
            return SECTION_MARKERS[line]
    return fallback


def extract_records(pdf_path: Path):
    doc = pymupdf.open(pdf_path)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    current_category = None
    current_section = None

    for page_index in range(START_PAGE - 1, END_PAGE):
        page = doc[page_index]
        page_no = page_index + 1
        page_text = page.get_text()
        (RAW_DIR / f'page-{page_no:03d}.txt').write_text(page_text, encoding='utf-8')

        new_category = detect_page_category(page_text, current_category)
        if new_category != current_category:
            current_section = None
        current_category = new_category
        current_section = detect_section(page_text, current_section)

        words = sorted(page.get_text('words'), key=lambda w: (w[1], w[0]))
        code_words = []
        for w in words:
            x0, y0, x1, y1, text, *_ = w
            if x0 < 60 and y0 > 170 and CODE_RE.match(text):
                code_words.append((text, y0))

        for idx, (code, y0) in enumerate(code_words):
            next_y = code_words[idx + 1][1] if idx + 1 < len(code_words) else 10_000
            y_min = y0 - 8
            y_max = next_y - 1
            text_y_max = next_y - 8

            name_lines = line_groups(words, 60, 136, y_min, text_y_max)
            source_lines = line_groups(words, 136, 190, y_min, text_y_max)
            name = norm_space(' '.join(name_lines))
            source = clean_source(' '.join(source_lines))

            numeric_map = {field: None for field, _ in COLUMN_SPECS}
            for w in words:
                x0, wy0, x1, y1, text, *_ = w
                if wy0 < y0 - 1 or wy0 > y0 + 3:
                    continue
                if x0 < 190:
                    continue
                num = parse_number(text)
                if num is None:
                    continue
                nearest_field = None
                nearest_dist = 999
                for field, center in COLUMN_SPECS:
                    dist = abs(x0 - center)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_field = field
                if nearest_field is not None and nearest_dist <= 13:
                    numeric_map[nearest_field] = num

            if not name or sum(v is not None for v in numeric_map.values()) < 10:
                continue

            record = {
                'code': code,
                'name': name,
                'source': source or None,
                'category': current_category,
                'section': current_section,
                'page_pdf': page_no,
            }
            record.update(numeric_map)
            records.append(record)

    return records


def write_csv(records, path: Path):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def write_json(records, path: Path):
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')


def write_sqlite(records, path: Path):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS foods')
    cols = ', '.join([
        'code TEXT PRIMARY KEY',
        'name TEXT',
        'source TEXT',
        'category TEXT',
        'section TEXT',
        'page_pdf INTEGER',
        *[f'{name} REAL' for name, _ in COLUMN_SPECS],
    ])
    cur.execute(f'CREATE TABLE foods ({cols})')
    placeholders = ', '.join(['?'] * len(FIELDNAMES))
    insert_cols = ', '.join(FIELDNAMES)
    cur.executemany(
        f'INSERT INTO foods ({insert_cols}) VALUES ({placeholders})',
        [[rec.get(field) for field in FIELDNAMES] for rec in records],
    )
    cur.execute('CREATE INDEX IF NOT EXISTS idx_foods_name ON foods(name)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_foods_category ON foods(category)')
    conn.commit()
    conn.close()


def write_summary(records, path: Path):
    categories = {}
    missing = {field: 0 for field, _ in COLUMN_SPECS}
    for rec in records:
        categories[rec['category']] = categories.get(rec['category'], 0) + 1
        for field, _ in COLUMN_SPECS:
            if rec.get(field) is None:
                missing[field] += 1
    summary = {
        'source_pdf_name': PDF_PATH.name,
        'page_range_pdf': f'{START_PAGE}-{END_PAGE}',
        'records': len(records),
        'categories': categories,
        'missing_counts': missing,
        'sample_codes': [rec['code'] for rec in records[:10]],
    }
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    records = extract_records(PDF_PATH)
    if not records:
        raise SystemExit('No records extracted.')
    write_csv(records, OUT_DIR / 'tkpi_2020_pages_15_83.csv')
    write_json(records, OUT_DIR / 'tkpi_2020_pages_15_83.json')
    write_sqlite(records, OUT_DIR / 'tkpi_2020_pages_15_83.sqlite')
    write_summary(records, OUT_DIR / 'summary.json')
    print(json.dumps({
        'ok': True,
        'out_dir': str(OUT_DIR),
        'records': len(records),
        'first': records[0],
        'last': records[-1],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
