#!/usr/bin/env python3
import os
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless-safe
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from matplotlib.font_manager import FontProperties

# ---------- Defaults ----------
COLOR_SCHEMES = {
    "white": {"PRIMARY": "#FFFFFF", "ACCENT": "#FFFFFF", "TEXT": "#FFFFFF"},
    "duke":  {"PRIMARY": "#00539B", "ACCENT": "#00539B", "TEXT": "#00539B"},
}

FONTFACE = "Gill Sans"

PNG_NAME = "carolina_logo.png"
JPG_NAME = "carolina_logo.jpg"
SVG_NAME = "carolina_logo.svg"

TILT_ANGLE = -60          # degrees
LW = 4.5                  # overall line width for arms and ellipse
ELLIPSE_WIDTH = 4.8       # total width
ELLIPSE_HEIGHT = 2.8      # total height
ARC_DEG = 20
ARC_START_DEG = -270 + ARC_DEG
ARC_END_DEG = 90 - ARC_DEG
ARC_LW = LW

# Spiral params
THETA_MAX = 2 * np.pi
ARM_PHASE = np.pi
B_SHAPE = 2.0
FILL = 0.92
LINEWIDTH = LW

# Arrow
ARROW_LEN = 2
ARROW_LW = 2.5

# Text
TITLE = "CAROLINA"
SUBTITLE = "Connecting Analyses and Research \n On Lensing and INtrinsic Alignments"
TITLE_FS = 40
SUB_FS = 20
ITAL_SUB = True


# ---------- Helpers ----------
def rot2d(theta_deg: float) -> np.ndarray:
    t = np.deg2rad(theta_deg)
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])

def normalized_spiral(theta, b=B_SHAPE):
    u = (1.0 + theta/THETA_MAX)
    r = (u**b - 1.0) / ((1.0 + 1.0)**b - 1.0)
    return np.clip(r, 0.0, 1.0)

def pts_to_figfrac(pts, fig_height_in):
    # 72 points = 1 inch
    return pts / (72.0 * fig_height_in)


def draw_logo(
    output_dir: str,
    color_mode: str,
    show_text: bool,
    dpi: int = 300,
    figsize=(8, 6),
    png_name: str = PNG_NAME,
    jpg_name: str = JPG_NAME,
    svg_name: str = SVG_NAME,
    fontface: str = FONTFACE,
):
    colors = COLOR_SCHEMES[color_mode]
    PRIMARY = colors["PRIMARY"]

    os.makedirs(output_dir, exist_ok=True)
    fig = plt.figure(figsize=figsize)

    # Reserve top band if showing text
    if show_text:
        text_band_pts = 1.1*TITLE_FS + 1.1*SUB_FS + 25
        top_pad = pts_to_figfrac(text_band_pts, figsize[1])
        axes_rect = [0.08, 0.08, 0.84, 1.0 - 0.08 - top_pad]
    else:
        axes_rect = [0.06, 0.06, 0.88, 0.88]

    ax = fig.add_axes(axes_rect)
    ax.set_aspect('equal')
    ax.axis('off')

    a = ELLIPSE_WIDTH / 2.0
    b = ELLIPSE_HEIGHT / 2.0

    theta = np.linspace(0, THETA_MAX, 1200)
    r1 = normalized_spiral(theta, b=B_SHAPE)
    x1 = r1 * np.cos(theta)
    y1 = r1 * np.sin(theta)

    r2 = normalized_spiral(theta, b=B_SHAPE)
    x2 = r2 * np.cos(theta + ARM_PHASE)
    y2 = r2 * np.sin(theta + ARM_PHASE)

    X1 = np.vstack([a * FILL * x1, b * FILL * y1])
    X2 = np.vstack([a * FILL * x2, b * FILL * y2])

    R = rot2d(TILT_ANGLE)
    arm1 = R @ X1
    arm2 = R @ X2

    # Spiral arms
    ax.plot(arm1[0], arm1[1], color=PRIMARY, lw=LINEWIDTH, solid_capstyle='round')
    ax.plot(arm2[0], arm2[1], color=PRIMARY, lw=LINEWIDTH, solid_capstyle='round')

    # C-shaped arc (envelope)
    tt = np.deg2rad(np.linspace(ARC_START_DEG, ARC_END_DEG, 400))
    x_e = (ELLIPSE_WIDTH / 2.0)  * np.cos(tt)
    y_e = (ELLIPSE_HEIGHT / 2.0) * np.sin(tt)
    arc = R @ np.vstack([x_e, y_e])
    ax.plot(arc[0], arc[1], color=PRIMARY, lw=ARC_LW, solid_capstyle='round')

    # Central bulge
    bulge_r = min(a, b) * 0.15
    ax.add_patch(Circle((0, 0), radius=bulge_r, facecolor=PRIMARY, edgecolor='none', zorder=0))

    # Arrow (wider head)
    start_local = np.array([0.0, -0.0])
    dir_local   = np.array([0.0, ARROW_LEN])
    R_ell = rot2d(TILT_ANGLE)
    start_rot = (R_ell @ start_local).tolist()
    end_rot   = (R_ell @ (start_local + dir_local)).tolist()

    arrow = FancyArrowPatch(
        start_rot, end_rot,
        arrowstyle='Simple,head_length=10,head_width=18,tail_width=3',
        linewidth=ARROW_LW, color=PRIMARY
    )
    ax.add_patch(arrow)

    # Text
    if show_text:
        title_fp = FontProperties(family=fontface, weight='light')
        sub_fp   = FontProperties(family=fontface, weight='light', style='italic' if ITAL_SUB else 'normal')

        band_bottom = axes_rect[1] + axes_rect[3]
        band_top    = 0.995

        fig_h_in = figsize[1]
        line_spacing = 1.15
        n_lines = len(SUBTITLE.split("\n"))

        title_h = (TITLE_FS / 72.0) / fig_h_in
        sub_h   = (n_lines * SUB_FS * line_spacing) / 72.0 / fig_h_in
        band_height = band_top - band_bottom
        G = max(0.0, (band_height - title_h - sub_h) / 2.0)

        title_y      = band_top
        subtitle_top = band_top - title_h - G
        sub_step     = (SUB_FS * line_spacing) / 72.0 / fig_h_in

        fig.text(0.5, title_y, "CAROLINA", fontproperties=title_fp,
                 ha='center', va='top', fontsize=TITLE_FS, color=PRIMARY)

        for i, line in enumerate(SUBTITLE.split("\n")):
            y = subtitle_top - i * sub_step
            fig.text(0.5, y, line, fontproperties=sub_fp,
                     ha='center', va='top', fontsize=SUB_FS, color=PRIMARY)

    # Frame
    margin = 1
    ax.set_xlim(-ELLIPSE_WIDTH/2 - margin, ELLIPSE_WIDTH/2 + margin)
    ax.set_ylim(-ELLIPSE_HEIGHT/2 - margin, ELLIPSE_HEIGHT/2 + margin)

    # Save
    suffix = "_text" if show_text else "_notext"
    c_sfx = "" if color_mode == "duke" else "_white"

    png_path = os.path.join(output_dir, PNG_NAME.replace(".png", f"{suffix}{c_sfx}.png"))
    jpg_path = os.path.join(output_dir, JPG_NAME.replace(".jpg", f"{suffix}{c_sfx}.jpg"))
    svg_path = os.path.join(output_dir, SVG_NAME.replace(".svg", f"{suffix}{c_sfx}.svg"))

    fig.savefig(png_path, dpi=dpi, bbox_inches='tight', transparent=True)
    fig.savefig(jpg_path, dpi=dpi, bbox_inches='tight', transparent=True)
    fig.savefig(svg_path, dpi=dpi, bbox_inches='tight', transparent=True)
    plt.close(fig)


def parse_args():
    p = argparse.ArgumentParser(description="Generate CAROLINA logo variants.")
    p.add_argument("--output-dir", default="docs/output_data/logo_output", help="Where to save images")
    p.add_argument("--dpi", type=int, default=300, help="Image DPI")
    p.add_argument("--figsize", type=float, nargs=2, default=(8, 6), metavar=("W", "H"),
                   help="Figure size inches W H")
    p.add_argument("--modes", nargs="+", default=["duke", "white"], choices=list(COLOR_SCHEMES.keys()),
                   help="Color modes to generate")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--with-text", dest="with_text", action="store_true", help="Generate ONLY text variants")
    group.add_argument("--no-text", dest="no_text", action="store_true", help="Generate ONLY no-text variants")
    # Default: both text + no-text if neither flag given
    return p.parse_args()


def main():
    args = parse_args()

    # Decide which text variants to make
    if args.with_text:
        text_variants = [True]
    elif args.no_text:
        text_variants = [False]
    else:
        text_variants = [True, False]

    for mode in args.modes:
        for show_text in text_variants:
            draw_logo(
                output_dir=args.output_dir,
                color_mode=mode,
                show_text=show_text,
                dpi=args.dpi,
                figsize=tuple(args.figsize),
            )
            print(f"Saved {mode} {'text' if show_text else 'notext'} variants to {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
