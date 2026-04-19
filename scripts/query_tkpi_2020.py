#!/usr/bin/env python3
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / 'data' / 'tkpi_2020_pages_15_83.sqlite'

query = ' '.join(sys.argv[1:]).strip()
if not query:
    raise SystemExit('Usage: query_tkpi_2020.py <search terms>')

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
rows = conn.execute(
    '''
    SELECT code, name, category, energy_kcal, protein_g, fat_g, carb_g, sodium_mg
    FROM foods
    WHERE name LIKE ? OR code LIKE ?
    ORDER BY CASE WHEN lower(name)=lower(?) THEN 0 ELSE 1 END, name
    LIMIT 20
    ''',
    (f'%{query}%', f'%{query}%', query),
).fetchall()
for row in rows:
    print(dict(row))
conn.close()
