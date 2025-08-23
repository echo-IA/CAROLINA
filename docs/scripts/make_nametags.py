#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import pandas as pd

# -------- helpers --------
def pts_to_axes_frac(pts, ax, fig):
    """Convert points to fraction of axes height (72 pt = 1 in)."""
    ax_h_in = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).height
    return (pts / 72.0) / ax_h_in

def logo_zoom_for_frac_height(img_array, target_axes_frac, ax, fig):
    """Zoom so image height == target_axes_frac of axes height."""
    ax_h_in = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).height
    REF_DPI = 100 # hardcoded to make the image fit, look at this later
    target_px = target_axes_frac * ax_h_in * REF_DPI
    img_px_h = img_array.shape[0]

    return max(0.01, target_px / img_px_h)

def main():
    # -------- paths --------
    INPUT_DIR = "docs/input_data"
    FILENAME  = "participant_list_web.csv"
    FILEPATH  = os.path.join(INPUT_DIR, FILENAME)

    # Use a high-res logo export (2–4× larger than needed) for crisp downscaling
    LOGO_PATH = "docs/output_data/logo_output/carolina_logo_notext.png"

    # -------- style --------
    COLOR = "#00539B"  # This is Duke Royal blue and this "#012169"  # Duke navy blue
    rcParams["font.family"] = "Helvetica, DejaVu Sans"
    rcParams["font.weight"] = "light"
    ITALIC = FontProperties(family="DejaVu Sans", style="italic")

    # -------- load & normalize data --------
    COLUMNS = ["Name", "Surname", "Affiliation", "Attendance"]
    df = pd.read_csv(FILEPATH, usecols=COLUMNS)
    df["Affiliation"] = (
        df["Affiliation"].astype(str).str.strip()
          .replace({
              r"(?i)^princeton$": "Princeton University",
              r"(?i)^northeastern$": "Northeastern University",
              r"(?i)^ucl$": "University College London",
          }, regex=True)
    )
    onsite = df[df["Attendance"].str.strip().str.lower() == "in person"]

    # -------- preload logo --------
    logo_img = plt.imread(LOGO_PATH)

    # -------- layout constants --------
    FIGSIZE = (7, 5)   # card size in inches

    TITLE_FS = 22
    SUB_FS = 10
    NAME_FS = 28
    AFFIL_FS = 14

    # Header band (top area that holds left text + right logo)
    HEADER_TOP = 0.90
    HEADER_BOTTOM = 0.62

    # Spacing controls (axes fractions / multipliers)
    TITLE_GAP_AX  = 0.08  # gap after CAROLINA
    SUB_LINE_MULT = 1.20  # subtitle line spacing × SUB_FS (in points)
    VENUE_GAP_AX  = 0.06  # gap between subtitle block and venue
    LOGO_MATCH_TEXT_BLOCK = True  # make logo height equal to 4-line text block

    # Left/right columns (axes fraction)
    TEXT_LEFT_X = 0.94
    TEXT_RIGHT_X = 0.8
    LOGO_CENTER_X = TEXT_RIGHT_X - 0.55

    # Name / affiliation gap (in points)
    NAME_GAP_PTS = 28
    ORGANIZERS = ["Sarcevic", "Blazek", "Joachimi", "Troxel", "Polen", "Teixeira", "Tierney"]

    OUTPUT_DIR = "docs/output_data/nametags"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # render only the first in-person participant while tuning ----
    #for _, row in onsite.head(1).iterrows():
    # to render all, use:
    for _, row in onsite.iterrows():
        fig, ax = plt.subplots(figsize=FIGSIZE)
        ax.axis("off")

        # Line heights in axes fraction
        sub_line_h_ax = pts_to_axes_frac(SUB_FS * SUB_LINE_MULT, ax, fig)
        title_h_ax = pts_to_axes_frac(TITLE_FS * 1.10, ax, fig)  # approximate line height
        sub_h_ax = pts_to_axes_frac(SUB_FS * 1.10,  ax, fig)

        # --- Left column: title + subtitle + venue (left-aligned) ---
        y = HEADER_TOP
        ax.text(TEXT_RIGHT_X, y, "CAROLINA", fontsize=TITLE_FS, fontweight="bold",
            ha="right", va="top", color=COLOR, transform=ax.transAxes)
        y -= TITLE_GAP_AX

        ax.text(TEXT_RIGHT_X, y, "Connecting Analyses and Research",
                fontsize=SUB_FS, ha="right", va="top",
                color=COLOR, transform=ax.transAxes, fontproperties=ITALIC)
        y -= sub_line_h_ax

        ax.text(TEXT_RIGHT_X, y, "On Lensing and INtrinsic Alignments",
                fontsize=SUB_FS, ha="right", va="top",
                color=COLOR, transform=ax.transAxes, fontproperties=ITALIC)
        y -= VENUE_GAP_AX

        ax.text(TEXT_RIGHT_X, y, "Duke University, September 15–19 2025",
                fontsize=SUB_FS, ha="right", va="top",
                color=COLOR, transform=ax.transAxes)

        # --- Right column: logo, height matched to the left text block ---
        header_height_ax = HEADER_TOP - HEADER_BOTTOM
        if LOGO_MATCH_TEXT_BLOCK:
            text_block_h_ax = (
                title_h_ax
                + TITLE_GAP_AX
                + sub_h_ax
                + sub_line_h_ax
                + sub_h_ax
                + VENUE_GAP_AX
                + sub_h_ax
            )
            logo_axes_frac_height = text_block_h_ax * 0.4   # e.g. 0.5

        zoom = logo_zoom_for_frac_height(logo_img, logo_axes_frac_height, ax, fig)
        img = OffsetImage(logo_img, zoom=zoom, interpolation="lanczos", resample=True)
        ab  = AnnotationBbox(
            img,
            (LOGO_CENTER_X, HEADER_TOP - 0.01),
            xycoords=ax.transAxes,
            frameon=False,
            box_alignment=(0.5, 1.0)
        )
        ax.add_artist(ab)

        # --- Name & Affiliation (centered below header band) ---
        below_gap_ax = 0.01
        name_gap_ax  = pts_to_axes_frac(NAME_GAP_PTS, ax, fig)

        y_block_start = HEADER_BOTTOM - below_gap_ax
        role = " (ORG)" if row["Surname"] in ORGANIZERS else ""
        full_name = f"{row['Name']} {row['Surname']}{role}".strip()

        ax.text(0.5, y_block_start, full_name, fontsize=NAME_FS, fontweight="bold",
                ha="center", va="top", color=COLOR, transform=ax.transAxes)

        y_affil = y_block_start - name_gap_ax
        ax.text(0.5, y_affil, str(row["Affiliation"]), fontsize=AFFIL_FS,
                ha="center", va="top", color=COLOR, transform=ax.transAxes)

        # Save
        safe_name = full_name.replace(" ", "_")
        out_png = os.path.join(OUTPUT_DIR, f"{safe_name}.png")
        plt.savefig(out_png, dpi=300, bbox_inches="tight")
        plt.close(fig)

    print(f"Nametags saved in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
