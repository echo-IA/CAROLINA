#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, html, textwrap
import pandas as pd
from data_utils import sort_participant_data  # uses your normalization/exclusion

def esc(v):
    return "" if pd.isna(v) else html.escape(str(v), quote=True)

def main():
    # ---- paths ----
    filename = "participant_list_web.csv"
    filepath = os.path.join("docs", "input_data", filename)
    outdir = os.path.join("docs", "pages")
    outfile = os.path.join(outdir, "participants.md")
    os.makedirs(outdir, exist_ok=True)

    # ---- load CSV ----
    cols = ["Name", "Surname", "Affiliation", "Attendance"]
    data = pd.read_csv(filepath, usecols=cols)

    # ---- clean, normalize, sort ----
    data_sorted = sort_participant_data(
        data,
        name="Name",
        surname="Surname",
        affiliation="Affiliation",
        attendance="Attendance",
    )

    # ---- build table ----
    headers = ["No.", "Participant", "Affiliation", "Attendance"]
    thead = "<thead>\n  <tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>\n</thead>"

    rows_html = []
    for i, (_, r) in enumerate(data_sorted.iterrows(), start=1):
        att_val = str(r.get("Attendance", "")).strip().lower()
        row_cls = "att-onsite" if att_val == "onsite" else ("att-online" if att_val == "online" else "att-unknown")
        full_name = f"{esc(r.get('Name', ''))} {esc(r.get('Surname', ''))}".strip()
        cells = (
            f"<td>{i}</td>"
            f"<td>{full_name}</td>"
            f"<td>{esc(r.get('Affiliation', ''))}</td>"
            f"<td>{esc(r.get('Attendance', ''))}</td>"
        )
        rows_html.append(f'<tr class="{row_cls}">{cells}</tr>')

    tbody = "<tbody>\n" + "\n".join(rows_html) + "\n</tbody>"
    table_html = f'<table class="participants-table">\n{thead}\n{tbody}\n</table>'

    # ---- attendance counts ----
    att_series = data_sorted["Attendance"].astype(str).str.strip().str.lower()
    n_onsite = (att_series == "onsite").sum()
    n_online = (att_series == "online").sum()
    n_total = len(att_series)
    n_unknown = n_total - n_onsite - n_online
    pct = lambda n: f"{(n / n_total * 100):.0f}%" if n_total else "0%"

    # ---- page bits ----
    front_matter = """---
layout: default
title: Participants
permalink: /participants/
order: 4
---
"""

    mini_menu = """
[Participants](#participants)
<br>
[Statistics](#statistics)

---
""".lstrip()

    # table + counts immediately after
    participants_section = textwrap.dedent(f"""
    <h2 id="participants">Workshop Participants</h2>
    {table_html}

    <h3 id="attendance-stats">Attendance stats</h3>
    <table class="stats-table">
      <thead><tr><th>Type</th><th>Count</th><th>%</th></tr></thead>
      <tbody>
        <tr><td>Onsite</td><td>{n_onsite}</td><td>{pct(n_onsite)}</td></tr>
        <tr><td>Online</td><td>{n_online}</td><td>{pct(n_online)}</td></tr>
        <tr><td>Unknown/Other</td><td>{n_unknown}</td><td>{pct(n_unknown)}</td></tr>
        <tr><td><strong>Total</strong></td><td><strong>{n_total}</strong></td><td>100%</td></tr>
      </tbody>
    </table>
    """).strip()

    # images section (Liquid + dedented so it renders as HTML)
    stats_section = textwrap.dedent("""
    ---

    <h2 id="statistics">Statistics</h2>
    <p align="center"><img src="{{ '/assets/images/collaborations_bar.jpg' | relative_url }}" width="1000"></p><br>
    <p align="center"><img src="{{ '/assets/images/rank_bar.jpg' | relative_url }}" width="1000"></p><br>
    """).lstrip()

    # ---- write file ----
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(front_matter + "\n" + mini_menu + "\n" + participants_section + "\n" + stats_section)

    print(f"Saved participants page to {outfile}")

if __name__ == "__main__":
    main()
