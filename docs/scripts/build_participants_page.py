#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html, os, textwrap, subprocess, sys
import pandas as pd
from pathlib import Path
from data_utils import sort_participant_data


def esc(v):
    return "" if pd.isna(v) else html.escape(str(v), quote=True)

def main():

    # --- first I build the stats plots ---
    here = Path(__file__).resolve().parent
    stats_script = here / "make_participant_stats.py"

    # --- run the stats script first ---
    try:
        subprocess.run([sys.executable, str(stats_script)], check=True)
        print("Stats images regenerated.")
    except Exception as e:
        print(f"Warning: could not build participant stats: {e}")

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

    # ---- attendance counts (added) ----
    att_series = data_sorted["Attendance"].astype(str).str.strip().str.lower()
    n_onsite = (att_series == "onsite").sum()
    n_online = (att_series == "online").sum()
    n_total  = len(att_series)
    n_unknown = n_total - n_onsite - n_online

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
<table class="participants-table">
  <thead>
    <tr><th>Type</th><th>Count</th></tr>
  </thead>
  <tbody>
    <tr class="att-onsite"><td>Onsite</td><td>{n_onsite}</td></tr>
    <tr class="att-online"><td>Online</td><td>{n_online}</td></tr>
    <tr class="att-unknown"><td>Unknown/Other</td><td>{n_unknown}</td></tr>
    <tr><td><strong>Total</strong></td><td><strong>{n_total}</strong></td></tr>
  </tbody>
</table>
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
