#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html, os, textwrap
import pandas as pd
from data_utils import sort_participant_data  # uses your normalization/exclusion

def esc(v):
    return "" if pd.isna(v) else html.escape(str(v), quote=True)

def main():
    # ---- paths ----
    filename = "participant_list_web.csv"
    filepath = os.path.join("docs", "input_data", filename)
    outdir = "docs/pages/"
    outfile = os.path.join(outdir, "participants.md")
    os.makedirs(outdir, exist_ok=True)

    # ---- load CSV ----
    cols = ["Name", "Surname", "Affiliation", "Attendance"]
    data = pd.read_csv(filepath, usecols=cols)

    # ---- clean, normalize, sort (excludes 'Tierney' by default) ----
    data_sorted = sort_participant_data(
        data,
        name="Name",
        surname="Surname",
        affiliation="Affiliation",
        attendance="Attendance",
    )

    # ---- build table with per-row class based on Attendance ----
    headers = ["No.", "Participant", "Affiliation", "Attendance"]
    thead = (
        "<thead>\n  <tr>"
        + "".join(f"<th>{h}</th>" for h in headers)
        + "</tr>\n</thead>"
    )

    rows_html = []
    for _, r in data_sorted.iterrows():
        att = str(r.get("Attendance", "")).strip().lower()
        row_cls = "att-onsite" if att == "onsite" else ("att-online" if att == "online" else "att-unknown")
        cells = "".join(
            f"<td>{esc(r.get(h, ''))}</td>" for h in headers
        )
        rows_html.append(f'<tr class="{row_cls}">{cells}</tr>')

    tbody = "<tbody>\n" + "\n".join(rows_html) + "\n</tbody>"

    table_html = f'''
<table class="participants-table">
{thead}
{tbody}
</table>'''.strip()

    # ---- attendance counts (add this) ----
    att_series = data_sorted["Attendance"].astype(str).str.strip().str.lower()
    n_onsite = (att_series == "onsite").sum()
    n_online = (att_series == "online").sum()
    n_total = len(att_series)

    # ---- page bits (same structure you asked for) ----
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

    participants_section = f"""
    <h2 id="participants">Workshop Participants</h2>
    {table_html}

    <h3 id="attendance-stats">Attendance stats</h3>
    <p><strong>Onsite:</strong> {n_onsite} &nbsp; | &nbsp; <strong>Online:</strong> {n_online} &nbsp; | &nbsp; <strong>Total:</strong> {n_total}</p>
    """.strip()

    stats_section = """
---

<h2 id="statistics">Statistics</h2>
<p align="center"><img src="{{ '/assets/images/collaborations_bar.jpg' | relative_url }}" width="1000"></p><br>
<p align="center"><img src="{{ '/assets/images/rank_bar.jpg' | relative_url }}" width="1000"></p><br>
""".lstrip()

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(front_matter)
        f.write("\n")
        f.write(mini_menu)
        f.write("\n")
        f.write(participants_section)
        f.write("\n")
        f.write(stats_section)

    print(f"Saved participants page to {outfile}")

if __name__ == "__main__":
    main()
