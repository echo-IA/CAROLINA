#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import matplotlib.pyplot as plt
import pandas as pd

def main():
    # -------- paths --------
    filename = 'participant_list_web.csv'
    filepath = f'docs/input_data/{filename}'
    outdir = 'docs/assets/images'
    os.makedirs(outdir, exist_ok=True)

    # -------- load data --------
    # Uncomment to inspect columns:
    # print(pd.read_csv(filepath).columns)

    columns_to_keep = ['Collaboration', 'Rank']
    data = pd.read_csv(filepath, usecols=columns_to_keep)

    # -------- colors --------
    duke_blue = "#00539B"   # Duke royal blue
    persimmon = "#E89923"   # orange
    piedmont  = "#A1B70D"   # green
    ironweed  = "#993399"   # purple
    color = duke_blue

    # ===== Collaborations bar chart =====
    collab_counts = (
        data['Collaboration']
        .fillna('')
        .astype(str)
        .str.replace(';', ',', regex=False)  # normalize separators
        .str.split(',')
        .explode()
        .str.strip()
        .loc[lambda s: s != '']              # drop blanks
        .value_counts()
    )

    # Filter out non-collaboration responses
    collab_counts = collab_counts.drop(['No', '(applied to become LSST DESC member)'], errors='ignore')

    # Sort descending
    collab_counts = collab_counts.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(16, 5))
    bars = ax.bar(collab_counts.index, collab_counts.values, color=piedmont)
    ax.bar_label(bars, fmt="%d", padding=5, fontsize=18, color=piedmont)

    ax.set_xlabel("Collaboration", fontsize=20, color=color)
    ax.set_ylabel("Number of participants", fontsize=20, color=color)
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontsize=16, color=color)
    plt.setp(ax.get_yticklabels(), fontsize=16, color=color)
    ax.tick_params(axis="both", colors=color)
    ax.margins(y=0.15)  # 15% extra space above tallest bar
    ax.tick_params(left=False, bottom=False)

    # Spines
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(color)

    plt.savefig(os.path.join(outdir, "collaborations_bar.jpg"),
                bbox_inches="tight", dpi=300, pad_inches=0.2)
    print(f"Participant stats saved in: {outdir}")

    # ===== Rank bar chart =====
    rank_series = data['Rank'].fillna("Unknown").astype(str).str.strip()

    # Normalize graduate labels (catch variants like "Graduate Student", "PhD student")
    def normalize_rank(r):
        r_low = r.lower()
        if "faculty" in r_low:
            return "Faculty"
        elif "postdoc" in r_low:
            return "Postdoc"
        elif "grad" in r_low or "phd" in r_low:
            return "Graduate"
        else:
            return "Other"

    rank_series = rank_series.apply(normalize_rank)

    # Count and sort
    rank_counts = rank_series.value_counts().drop("Staff", errors="ignore").sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(14, 5))
    # Map colors per category
    rank_colors = {
        "Faculty": piedmont,
        "Postdoc": persimmon,
        "Graduate": ironweed,
        "Other": "#FDDA0D"
    }
    bar_colors = [rank_colors.get(rank, "yellow") for rank in rank_counts.index]

    bars = ax.bar(rank_counts.index, rank_counts.values, color=bar_colors)

    # Labels on bars (match each bar’s color)
    for bar, val, c in zip(bars, rank_counts.values, bar_colors):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val}", ha="center", va="bottom", fontsize=16, color=c)

    ax.set_xlabel("Academic Rank", fontsize=20, color=color)
    ax.set_ylabel("Number of participants", fontsize=20, color=color)
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontsize=18, color=color)
    plt.setp(ax.get_yticklabels(), fontsize=18, color=color)
    ax.tick_params(axis="both", colors=color, left=False, bottom=False)
    ax.margins(y=0.15)

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(color)

    plt.savefig(os.path.join(outdir, "rank_bar.jpg"),
                bbox_inches="tight", dpi=300, pad_inches=0.2)
    print(f"Participant stats saved in: {outdir}")


if __name__ == "__main__":
    main()
