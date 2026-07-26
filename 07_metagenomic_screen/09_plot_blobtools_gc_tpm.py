#!/usr/bin/env python3
"""
BlobTools-style GC% x TPM figure, restyled to match the paper's house visual
language (Arial, colorblind-safe categorical palette, panel title convention).
Highlights the Sulcia/Sodalis endosymbiont candidates against the rest of the
annotated transcriptome to test the AT-rich genome signature reported in the
literature for Sulcia (Bennett & Moran 2013).

Exports: blobplot_gc_tpm.png (300 dpi) and .tiff (300 dpi)

Data source (verified against file on disk, not re-derived):
  - 07_metagenomic_screen/results/blobtools_gc_tpm/gc_tpm_table.tsv
    (GC% via seqkit fx2tab, TPM via Salmon, category via annotation_complete.tsv
    + endosymbiont_candidates/sulcia_sodalis_hits.tsv)

Usage:
  python 07_metagenomic_screen/09_plot_blobtools_gc_tpm.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "results", "blobtools_gc_tpm", "gc_tpm_table.tsv")

CAT_COLORS = {
    "Eukaryota":                 "#BDBDBD",
    "Fungi":                     "#F07D0C",
    "unclassified":              "#E8E8E8",
    "Sulcia/Sodalis candidate":  "#1A9641",
}
CAT_ORDER = ["unclassified", "Eukaryota", "Fungi", "Sulcia/Sodalis candidate"]
CAT_ZORDER = {"unclassified": 2, "Eukaryota": 3, "Fungi": 4, "Sulcia/Sodalis candidate": 6}
CAT_SIZE = {"unclassified": 5, "Eukaryota": 6, "Fungi": 8, "Sulcia/Sodalis candidate": 26}
CAT_ALPHA = {"unclassified": 0.25, "Eukaryota": 0.35, "Fungi": 0.55, "Sulcia/Sodalis candidate": 0.95}

plt.rcParams.update({
    "font.family":       "Arial",
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   8.5,
    "axes.linewidth":    0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

df = pd.read_csv(TABLE, sep="\t")
df["log_tpm"] = np.log10(df["TPM"].fillna(0) + 1)

euk = df.loc[df["category"] == "Eukaryota", "gc"]
sul = df.loc[df["category"] == "Sulcia/Sodalis candidate", "gc"]
stat, pval = mannwhitneyu(sul, euk, alternative="less")

fig, ax = plt.subplots(figsize=(9, 6.5))
fig.subplots_adjust(left=0.10, right=0.97, top=0.86, bottom=0.11)

for cat in CAT_ORDER:
    sub = df[df["category"] == cat]
    ax.scatter(sub["gc"], sub["log_tpm"], s=CAT_SIZE[cat], alpha=CAT_ALPHA[cat],
               c=CAT_COLORS[cat], zorder=CAT_ZORDER[cat],
               edgecolors="#333333" if cat == "Sulcia/Sodalis candidate" else "none",
               linewidths=0.5,
               label=f"{cat}  (n={len(sub)})")

ax.axvline(euk.median(), color="#666666", lw=0.9, ls="--", zorder=1)
ax.axvline(sul.median(), color="#1A9641", lw=1.3, ls="--", zorder=5)
ax.text(euk.median() + 0.5, ax.get_ylim()[1] * 0.96, f"mediana Eukaryota\n{euk.median():.1f}%",
        fontsize=7.8, color="#555555", va="top")
ax.text(sul.median() - 0.5, ax.get_ylim()[1] * 0.96, f"mediana Sulcia/Sodalis\n{sul.median():.1f}%",
        fontsize=7.8, color="#1A9641", va="top", ha="right", fontweight="bold")

ax.set_xlabel("GC% do contig")
ax.set_ylabel("log10(TPM + 1)  [proxy de cobertura via expressao Salmon]")
ax.set_title(
    "GC% x TPM por contig -- candidatos Sulcia/Sodalis destacados\n"
    f"Mann-Whitney (Sulcia/Sodalis < Eukaryota): p = {pval:.1e}",
    loc="left", fontweight="bold", fontsize=11, pad=10)
ax.grid(color="#eeeeee", lw=0.5, zorder=0)
ax.legend(loc="upper right", frameon=False, fontsize=8.3, markerscale=1.4)

# --- save ---------------------------------------------------------------------

outdir = os.path.join(HERE, "results", "blobtools_gc_tpm")
base = os.path.join(outdir, "blobplot_gc_tpm")

fig.savefig(base + ".png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(base + ".tiff", dpi=300, bbox_inches="tight", facecolor="white")

print("Saved:")
print("  " + base + ".png  (300 dpi)")
print("  " + base + ".tiff (300 dpi)")
print(f"N Eukaryota={len(euk)} median={euk.median():.2f} | N Sulcia/Sodalis={len(sul)} median={sul.median():.2f} | p={pval:.3e}")
