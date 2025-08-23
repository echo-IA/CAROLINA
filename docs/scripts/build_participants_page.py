#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd

# ---------- helpers ----------
def transform_attendance(series: pd.Series) -> pd.Series:
    mapping = {"in person": "Onsite", "online": "Online"}
    return series.apply(
        lambda x: mapping.get(str(x).strip().lower(), x) if pd.notnull(x) else x
    )

def extract_surname(full_name: str) -> str:
    if not isinstance(full_name, str) or not full_name.strip():
        return ""
    parts = full_name.split()
    parts.reverse()
    surname_parts = [parts[0]]
    prefixes = {
        "van", "van der", "Van", "van de", "de", "le", "la",
        "von", "da", "del", "della", "di",
    }
    # walk backwards, accumulate known prefixes
    acc = []
    i = 1
    while i < len(parts):
        # try two-word prefix first
        two = (parts[i] + " " + parts[i+1]).lower() if i + 1 < len(parts) else ""
        if two in prefixes:
            acc.append(parts[i+1])
            acc.append(parts[i])
            i += 2
            continue
        # then single
        if parts[i].lower() in prefixes:
            acc.append(parts[i])
            i += 1
            continue
        break
    surname = " ".join(reversed([*acc, surname_parts[0]])).strip()
    return surname

def sort_participant_data(df: pd.DataFrame,
                          name="Name", surname="Surname",
                          affiliation="Affiliation", attendance="Attendance") -> pd.DataFrame:
    # normalize attendance
    if attendance in df.columns:
        df[attendance] = transform_attendance(df[attendance])
    # Participant column
    df["Participant"] = (
        df.get(name, "").fillna("").astype(str).str.strip()
        + " "
        + df.get(surname, "").fillna("").astype(str).str.strip()
    ).str.strip()
    # add computed Surname for sorting
    df["__SurnameKey"] = df["Participant"].apply(extract_surname)
    df = df.sort_values(by="__SurnameKey").drop(columns="__SurnameKey")
    # numbering
    df["No."] = range(1, len(df) + 1)
    # select final order
    cols_out = ["No.", "Participant"]
    if affiliation in df.columns: cols_out.append(affiliation)
    if attendance in df.columns: cols_out.append(attendance)
    return df[cols_out].reset_index(drop=True)

def build_page_md(data_sorted: pd.DataFrame, images: list[str]) -> str:
    # --- keep your exact header/links block ---
    header = """---
layout: default
title: Participants
order: 4
---


[Participants](#participants)
<br>
[Statistics](#statistics)

---


"""
    # participants table
    table_html = data_sorted.to_html(
        index=False, border=0, classes="participants-table", escape=False
    )

    participants_block = f"""<h2 id="participants">Workshop Participants</h2>
{table_html}

---

"""

    # statistics block
    stats_block = ""
    if images:
        stats_imgs = "\n".join(
            f'<p align="center"><img src="{img}" width="1000"></p><br>'
            for img in images
        )
        stats_block = f"""<h2 id="statistics">Statistics</h2>
{stats_imgs}
"""

    return header + participants_block + stats_block

# ---------- main ----------
def main():
    parser = argparse.ArgumentParser(description="Build participants.md from CSV")
    parser.add_argument("--csv", default="docs/input_data/participant_list_web.csv",
                        help="Path to participant CSV (default: docs/input_data/participant_list_web.csv)")
    parser.add_argument("--output", default="docs/participants.md",
                        help="Path to output participants.md (default: docs/participants.md)")
    parser.add_argument("--images", nargs="*", default=[
        "assets/images/collaborations_bar.jpg",
        "assets/images/rank_bar.jpg",
    ], help="Optional stats image paths")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    out_path = Path(args.output)

    # columns to keep if present
    usecols = ["Name", "Surname", "Affiliation", "Attendance"]
    df = pd.read_csv(csv_path, usecols=[c for c in usecols if c in pd.read_csv(csv_path, nrows=0).columns])
    data_sorted = sort_participant_data(df)

    md = build_page_md(data_sorted, images=args.images)
    out_path.write_text(md, encoding="utf-8")
    print(f"Wrote {out_path.resolve()} with {len(data_sorted)} participants.")

if __name__ == "__main__":
    main()
