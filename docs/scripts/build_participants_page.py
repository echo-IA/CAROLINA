#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd

# Import your helpers
from data_utils import sort_participant_data  # build_participants_html not used here

def main():
    # ---- paths ----
    filename = "participant_list_web.csv"
    filepath = os.path.join("docs", "input_data", filename)
    outdir = "docs"
    outfile = os.path.join(outdir, "participants.md")
    os.makedirs(outdir, exist_ok=True)

    # ---- load & filter CSV ----
    columns_to_keep = ["Name", "Surname", "Affiliation", "Attendance"]
    data = pd.read_csv(filepath, usecols=columns_to_keep)

    # ---- clean/sort via your helper ----
    data_sorted = sort_participant_data(
        data,
        name="Name",
        surname="Surname",
        affiliation="Affiliation",
        attendance="Attendance",
    )

    # ---- HTML table ----
    table_html = data_sorted.to_html(
        index=False,
        border=0,
        classes="dataframe participants-table",
        escape=False,
    )

    # ---- page pieces (exact per your spec) ----
    front_matter = """---
layout: default
title: Participants
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
""".strip()

    # images at the bottom
    stats_section = """
---

<h2 id="statistics">Statistics</h2>
<p align="center"><img src="assets/images/collaborations_bar.jpg" width="1000"></p><br>
<p align="center"><img src="assets/images/rank_bar.jpg" width="1000"></p><br>
""".lstrip()

    # ---- write file ----
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
