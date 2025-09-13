#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import datetime, html, math, os, re


DAY_ORDER = {"monday":0,"tuesday":1,"wednesday":2,"thursday":3,"friday":4}

def parse_time_to_minutes(s: str) -> int:
    """Return minutes since midnight from a 'Time (EDT)' cell.
    Handles '9', '9:30', '09:30', '9–10', '9:30-10:15', '9 am', '1 pm', etc."""
    if not s: return 10**9  # push empties to bottom
    s = str(s).strip().lower()

    # grab the *first* time in the cell (start time)
    # matches H, H:MM, with optional am/pm; allows spaces
    m = re.search(r'(\d{1,2})(?::(\d{2}))?\s*([ap]\.?m\.?)?', s)
    if not m:
        return 10**9

    h = int(m.group(1))
    mm = int(m.group(2) or 0)
    ampm = m.group(3)

    if ampm:
        ampm = ampm.replace('.', '')
        if ampm == 'pm' and h < 12: h += 12
        if ampm == 'am' and h == 12: h = 0
    # else: assume 24h-style if no am/pm

    return h*60 + mm


def main():
    # ---- Robust CSV read ----
    df = pd.read_csv(
        'docs/input_data/carolina_schedule.csv',
        encoding='utf-8-sig',        # strips BOM if present
        skip_blank_lines=True,
        dtype=str,                   # read everything as strings first
        keep_default_na=False        # don't auto-convert "nan"/"NaN" strings
    )

    # Strip whitespace from column names, drop fully empty extra columns
    df.columns = df.columns.str.strip()
    df = df.dropna(axis=1, how='all')

    # If there are trailing-commas columns, they'll be named like 'Unnamed: N'
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

    # Keep only the columns you expect (after normalizing their names)
    expected = ['Day', 'Time (EDT)', 'Location', 'Event', 'Speaker']
    missing = [c for c in expected if c not in df.columns]
    if missing:
        print("WARNING: Missing expected columns:", missing)
    df = df.reindex(columns=expected)

    # Normalize cell strings: strip, convert empty/whitespace/'nan' to NA
    df = df.map(lambda x: None if (x is None or str(x).strip().lower() in {'', 'nan', 'none', '--'}) else str(x).strip())

    # ---- The rest (same as your builder) ----
    def safe(v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return '--'
        return html.escape(str(v), quote=True)

    def day_key(s):
        m = re.search(r'(monday|tuesday|wednesday|thursday|friday)', str(s), re.I)
        return m.group(1).lower() if m else str(s).strip().lower()

    order_keys   = ['monday','tuesday','wednesday','thursday','friday']
    display_name = {k: k.capitalize() for k in order_keys}
    day_class    = {
        'monday':    'day-observations',
        'tuesday':   'day-theory',
        'wednesday': 'day-hack',
        'thursday':  'day-sims',
        'friday':    'day-hack',
    }
    day_focus = {
        'monday':    'Observations',
        'tuesday':   'Modeling',
        'wednesday': 'Hack Day',
        'thursday':  'Simulations',
        'friday':    'Hack Day',
    }

    # ---- canonicalize day + time and sort globally ----
    keys_in_csv = df['Day'].apply(day_key)
    df['__day_key'] = keys_in_csv
    df['__day_ord'] = df['__day_key'].map(DAY_ORDER).fillna(9999).astype(int)
    df['__time_ord'] = df['Time (EDT)'].apply(parse_time_to_minutes)

    df = df.sort_values(['__day_ord', '__time_ord', 'Location', 'Event'], na_position='last')


    # derive present days
    keys_in_csv = df['Day'].apply(day_key)
    present = [k for k in ['monday','tuesday','wednesday','thursday','friday'] if (df['__day_key'] == k).any()]

    table_headers = ['Time (EDT)', 'Location', 'Event', 'Speaker']
    tables_html = []

    for k in present:
        day_df = df[df['__day_key'] == k]
        if day_df.empty:
            continue

        cls   = day_class.get(k, 'day-default')
        aid   = k
        title = display_name.get(k, k.capitalize())
        focus = day_focus.get(k, '')

        rows = []
        for _, r in day_df.iterrows():
            cells = ''.join(f"<td>{safe(r[col])}</td>" for col in table_headers)
            rows.append(f"<tr>{cells}</tr>")

        heading_html = html.escape(title)
        if focus:
            heading_html += f' — <span class="schedule-focus">Focus: {html.escape(focus)}</span>'

        table_html = f"""
<h2 id="{aid}" class="schedule-day {cls}">{heading_html}</h2>
<table class="schedule-table {cls}">
  <thead>
    <tr>
      {''.join(f'<th>{html.escape(h)}</th>' for h in table_headers)}
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
""".strip()
        tables_html.append(table_html)

    html_schedule = "\n\n".join(tables_html)
    print(html_schedule)

    # ---- Write schedule.md with the provided front matter and intro ----
    md_header = """---
layout: default
title: Schedule
order: 3
---

# Schedule

The location for these sessions is the [Mary Duke Biddle Center for Health Education](https://www.google.com/maps?client=firefox-b-1-d&sca_esv=c48dc88e8766c10f&output=search&q=mary+duke+biddle+trent+semans+center+for+health+education&source=lnms&fbs=AIIjpHxU7SXXniUZfeShr2fp4giZ1Y6MJ25_tmWITc7uy4KIehZSPZtqywdxHK81a_1UWmZHKJ6oqjHuUktiabrRPeHJMsvLtH8GNAdGHXBY55oOcQgKj85Zt8V0rJBqqM2jRLVOpwhMemqaFe_3JlhfsrbwzIEzn71Fr66wXjX2eFkeBIwcD5fliuxdO7E3jZZwFrqx1YiZL2nX8zmQMDFMNA9nTTfsA&entry=mc&ved=1t:200715&ictx=111).

Participants are welcome to meet/work before and after the scheduled events.
The Mary Duke Biddle Trent Semans Center for Health Education is typically open from 8am to 5pm
during the week.
All times are in EDT and the in-person location is the Center for Health Education unless otherwise marked.


---

[Monday](#monday)
<br>
[Tuesday](#tuesday)
<br>
[Wednesday](#wednesday)
<br>
[Thursday](#thursday)
<br>
[Friday](#friday)
<br>

---

"""
    outpath = os.path.join("docs", "pages", "schedule.md")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(md_header)
        f.write(html_schedule)
        f.write("\n")

    print(f"Saved schedule page to {outpath}")


if __name__ == "__main__":
    main()
