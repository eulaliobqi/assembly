#!/usr/bin/env python3
"""
Publication-quality annotation summary figure.
Exports: annotation_summary.png (300 dpi) and annotation_summary.tiff (600 dpi)

Usage:
  python plot_annotation.py --report results/annotation_report.txt
  python plot_annotation.py  # uses hardcoded values from the run
"""

import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np

# --- data (from the pipeline report) -----------------------------------------

TOTAL = 12445

ANNOTATION = {
    "DIAMOND\nhits":    9340,
    "GO\nterms":        9197,
    "KEGG\northologs":  9197,
    "Pfam\ndomains":    7732,
}

TAXONOMY = {
    "Eukaryota":    8455,
    "Unclassified": 3164,
    "Bacteria":     540,
    "Fungi":        256,
    "Viruses":      30,
}

# --- color palettes (colorblind-safe) ----------------------------------------

BAR_COLOR   = "#2C7BB6"
BAR_REST    = "#D9E8F5"

TAX_COLORS  = {
    "Eukaryota":    "#2C7BB6",
    "Bacteria":     "#D7191C",
    "Fungi":        "#F07D0C",
    "Viruses":      "#1A9641",
    "Unclassified": "#BDBDBD",
}

# --- figure setup -------------------------------------------------------------

plt.rcParams.update({
    "font.family":       "Arial",
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
    "axes.linewidth":    0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

fig = plt.figure(figsize=(10, 5))
gs  = GridSpec(1, 2, figure=fig, wspace=0.38, left=0.08, right=0.97,
               top=0.88, bottom=0.22)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# --- panel A: horizontal stacked bar (annotated vs unannotated) ---------------

labels = list(ANNOTATION.keys())
values = list(ANNOTATION.values())
unanno = [TOTAL - v for v in values]
pcts   = [100.0 * v / TOTAL for v in values]

y = np.arange(len(labels))
bar_h = 0.55

b1 = ax1.barh(y, values, height=bar_h, color=BAR_COLOR,  label="Annotated",   zorder=3)
b2 = ax1.barh(y, unanno, height=bar_h, left=values,
              color=BAR_REST, label="Not annotated", zorder=3)

# percentage labels inside bars
for i, (v, p) in enumerate(zip(values, pcts)):
    ax1.text(v / 2, i, "%.1f%%" % p,
             ha="center", va="center", fontsize=9,
             color="white", fontweight="bold")

ax1.set_yticks(y)
ax1.set_yticklabels(labels)
ax1.set_xlabel("Number of proteins")
ax1.set_xlim(0, TOTAL * 1.04)
ax1.set_title("A   Functional annotation coverage", loc="left",
              fontweight="bold", pad=6)
ax1.axvline(TOTAL, color="#999999", lw=0.7, ls="--", zorder=2)
ax1.text(TOTAL + 350, -0.65, "n = %s" % f"{TOTAL:,}",
         fontsize=8, color="#555555", va="bottom")
ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18),
           frameon=False, ncol=2, handlelength=1.2, handletextpad=0.5)
ax1.tick_params(axis="y", length=0)
ax1.grid(axis="x", color="#e0e0e0", lw=0.5, zorder=0)

# --- panel B: donut chart (taxonomic origin) ----------------------------------

tax_labels = list(TAXONOMY.keys())
tax_vals   = list(TAXONOMY.values())
tax_colors = [TAX_COLORS[k] for k in tax_labels]

wedge_props = dict(width=0.48, edgecolor="white", linewidth=1.2)
wedges, texts = ax2.pie(
    tax_vals,
    colors=tax_colors,
    startangle=90,
    counterclock=False,
    wedgeprops=wedge_props,
)

# center annotation
ax2.text(0, 0, f"{TOTAL:,}\nproteins",
         ha="center", va="center", fontsize=9.5,
         fontweight="bold", color="#333333",
         multialignment="center")

# legend with counts and percentages
legend_labels = [
    "%s  %s (%.1f%%)" % (k, f"{v:,}", 100.0 * v / TOTAL)
    for k, v in zip(tax_labels, tax_vals)
]
patches = [mpatches.Patch(color=c, label=l)
           for c, l in zip(tax_colors, legend_labels)]
ax2.legend(handles=patches, loc="lower center",
           bbox_to_anchor=(0.5, -0.22),
           frameon=False, ncol=1,
           handlelength=1.0, handletextpad=0.5,
           labelspacing=0.35)

ax2.set_title("B   Taxonomic origin of best hits", loc="left",
              fontweight="bold", pad=6)

# --- save ---------------------------------------------------------------------

outdir = os.path.dirname(os.path.abspath(__file__))
base   = os.path.join(outdir, "annotation_summary")

fig.savefig(base + ".png",  dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(base + ".tiff", dpi=300, bbox_inches="tight", facecolor="white")

print("Saved:")
print("  " + base + ".png  (300 dpi)")
print("  " + base + ".tiff (300 dpi)")
