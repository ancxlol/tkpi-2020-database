#!/usr/bin/env python3
import json
import re
import sqlite3
import sys
from pathlib import Path

import pymupdf

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PDF = 'Buku Tabel Komposisi Pangan Indonesia tahun 2020.pdf'
PDF_PATH = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path(DEFAULT_PDF)
DB_PATH = ROOT_DIR / 'data' / 'tkpi_2020_pages_15_83.sqlite'
OUT_PATH = ROOT_DIR / 'validation_sample.json'

CODE_RE = re.compile(r'^[A-Z]{2}\d{3}$')
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

SAMPLE_CODES = [
    'AR001','AP001','BP001','CP076','DP001','EP001','FP001',
    'GP001','HP001','JP001','KP001','MP001','NP001','QR001'
]


def norm_space(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def clean_source(text: str) -> str:
    s = norm_space(text)
    return re.sub(r'\s*-\s*', '-', s)


def parse_number(text: str):
    text = text.strip().replace(',', '.')
    if not text:
        return None
    try:
        if '.' in text:
            return float(text)
        return int(text)
    except ValueError:
        return None


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


def extract_row_from_pdf(doc, page_no, code):
    page = doc[page_no - 1]
    words = sorted(page.get_text('words'), key=lambda w: (w[1], w[0]))
    code_words = [(w[4], w[1]) for w in words if w[0] < 60 and w[1] > 170 and CODE_RE.match(w[4])]
    idx = next(i for i, (c, _) in enumerate(code_words) if c == code)
    _, y0 = code_words[idx]
    next_y = code_words[idx + 1][1] if idx + 1 < len(code_words) else 10_000
    y_min = y0 - 8
    text_y_max = next_y - 8

    name = norm_space(' '.join(line_groups(words, 60, 136, y_min, text_y_max)))
    source = clean_source(' '.join(line_groups(words, 136, 190, y_min, text_y_max)))

    numeric_map = {field: None for field, _ in COLUMN_SPECS}
    for w in words:
        x0, wy0, x1, y1, text, *_ = w
        if wy0 < y0 - 1 or wy0 > y0 + 3 or x0 < 190:
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
        if nearest_field and nearest_dist <= 13:
            numeric_map[nearest_field] = num

    return {
        'code': code,
        'name': name,
        'source': source,
        **numeric_map,
    }


def main():
    if not PDF_PATH.exists():
        raise SystemExit(f'Source PDF not found: {PDF_PATH}')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    doc = pymupdf.open(PDF_PATH)

    results = []
    failures = []
    fields_to_check = ['name','source','energy_kcal','protein_g','fat_g','carb_g','sodium_mg']

    for code in SAMPLE_CODES:
        db_row = conn.execute('SELECT * FROM foods WHERE code=?', (code,)).fetchone()
        if not db_row:
            failures.append({'code': code, 'error': 'missing from database'})
            continue
        db_row = dict(db_row)
        pdf_row = extract_row_from_pdf(doc, db_row['page_pdf'], code)
        mismatches = {}
        for field in fields_to_check:
            db_val = db_row.get(field)
            pdf_val = pdf_row.get(field)
            if isinstance(db_val, float) and pdf_val is not None:
                if abs(db_val - float(pdf_val)) > 1e-9:
                    mismatches[field] = {'db': db_val, 'pdf': pdf_val}
            else:
                if db_val != pdf_val:
                    mismatches[field] = {'db': db_val, 'pdf': pdf_val}
        item = {
            'code': code,
            'page_pdf': db_row['page_pdf'],
            'matched': not mismatches,
            'mismatches': mismatches,
            'db': {field: db_row.get(field) for field in fields_to_check},
            'pdf': {field: pdf_row.get(field) for field in fields_to_check},
        }
        results.append(item)
        if mismatches:
            failures.append({'code': code, 'mismatches': mismatches})

    payload = {
        'source_pdf_name': PDF_PATH.name,
        'database_file': DB_PATH.name,
        'sample_codes': SAMPLE_CODES,
        'checked': len(results),
        'passed': len(failures) == 0,
        'failures': failures,
        'results': results,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'passed': payload['passed'], 'checked': len(results), 'failures': failures}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
