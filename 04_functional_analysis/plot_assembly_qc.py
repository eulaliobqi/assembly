#!/usr/bin/env python3
"""
Didactic assembly QC summary figure: Trinity/CD-HIT-EST size, Nx curve, BUSCO,
TransDecoder ORF types.

Exports: assembly_qc_summary.png (300 dpi) and .tiff (300 dpi)

Data source (verified against files on disk, not re-derived):
  - 02_assembly_evaluation/trinity_stats2.txt (genes, transcripts, Nx, GC, bases)
  - 02_assembly_evaluation/busco/short_summary...txt (BUSCO C/S/D/F/M)
  - data/transdecoder/trinity_nr95.fasta.transdecoder.pep headers (ORF type: counts)

Usage:
  python plot_assembly_qc.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

# --- data (verified against files on disk) ------------------------------------

N_GENES = 90344
N_TRANSCRIPTS = 103560
N_PROTEINS = 12445
GC_PCT = 34.21

NX = {"N10": 3990, "N20": 2465, "N30": 1654, "N40": 1101, "N50": 738}

BUSCO = {
    "Complete\n(single-copy)": 545,
    "Complete\n(duplicated)": 770,
    "Fragmented": 26,
    "Missing": 26,
}
BUSCO_N = 1367

ORF_TYPES = {
    "Complete": 7262,
    "5'-partial": 2026,
    "Internal": 1986,
    "3'-partial": 1171,
}

# --- colors (colorblind-safe, consistent with plot_annotation.py) -------------

STAGE_COLOR = "#2C7BB6"
NX_COLOR = "#2C7BB6"
NX_HIGHLIGHT = "#D7191C"
BUSCO_COLORS = ["#1A9641", "#A6D96A", "#F07D0C", "#D7191C"]
ORF_COLORS = ["#2C7BB6", "#7FB3D5", "#F07D0C", "#BDBDBD"]

plt.rcParams.update({
    "font.family":       "Arial",
    "font.size":         11,
    "axes.titlesize":    12,
    "axes.labelsize":    11,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "legend.fontsize":   9.5,
    "axes.linewidth":    0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

fig = plt.figure(figsize=(11, 8.5))
gs = GridSpec(2, 2, figure=fig, wspace=0.32, hspace=0.48,
              left=0.08, right=0.97, top=0.92, bottom=0.08)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])

# --- panel A: pipeline funnel (Trinity+CD-HIT-EST 95% -> TransDecoder) --------

stages = ["Trinity + CD-HIT-EST 95%\n(transcritos nao-redundantes)",
          "TransDecoder\n(--single_best_only)"]
stage_vals = [N_TRANSCRIPTS, N_PROTEINS]

y = np.arange(len(stages))
bars = ax1.barh(y, stage_vals, height=0.5, color=STAGE_COLOR, zorder=3)
for i, v in enumerate(stage_vals):
    ax1.text(v + max(stage_vals) * 0.015, i, f"{v:,}",
              va="center", fontsize=11, fontweight="bold", color="#222222")
ax1.set_yticks(y)
ax1.set_yticklabels(stages)
ax1.set_xlabel("Numero de sequencias")
ax1.set_xlim(0, max(stage_vals) * 1.22)
ax1.set_title("A   Do transcrito a proteina", loc="left", fontweight="bold", pad=8)
ax1.text(0, -0.85,
          f"{N_GENES:,} genes Trinity  |  GC {GC_PCT}%  |  reducao de "
          f"redundancia: 12.857 transcritos colapsados por similaridade >=95%",
          fontsize=9, color="#555555")
ax1.grid(axis="x", color="#e0e0e0", lw=0.5, zorder=0)
ax1.tick_params(axis="y", length=0)

# --- panel B: Nx curve (contig length vs. cumulative assembly fraction) -------

labels = list(NX.keys())
vals = list(NX.values())
xpos = np.arange(len(labels))
colors = [NX_HIGHLIGHT if lbl == "N50" else NX_COLOR for lbl in labels]

ax2.bar(xpos, vals, color=colors, width=0.6, zorder=3)
for i, v in enumerate(vals):
    ax2.text(i, v + 60, f"{v:,} pb", ha="center", fontsize=10, fontweight="bold")
ax2.set_xticks(xpos)
ax2.set_xticklabels(labels)
ax2.set_ylabel("Comprimento do contig (pb)")
ax2.set_title("B   Curva Nx: N50 = 738 pb", loc="left", fontweight="bold", pad=8)
ax2.text(0.5, -0.32,
          "N50: 50% das bases montadas estao em contigs >= 738 pb",
          transform=ax2.transAxes, ha="center", fontsize=9.5, color="#555555")
ax2.grid(axis="y", color="#e0e0e0", lw=0.5, zorder=0)
ax2.set_ylim(0, max(vals) * 1.22)

# --- panel C: BUSCO completeness (stacked horizontal bar) --------------------

busco_labels = list(BUSCO.keys())
busco_vals = list(BUSCO.values())
busco_pcts = [100.0 * v / BUSCO_N for v in busco_vals]

left = 0
for lbl, v, pct, c in zip(busco_labels, busco_vals, busco_pcts, BUSCO_COLORS):
    ax3.barh(0, v, left=left, height=0.5, color=c, edgecolor="white",
              linewidth=1.0, zorder=3)
    if pct >= 3:
        ax3.text(left + v / 2, 0, f"{pct:.1f}%", ha="center", va="center",
                  fontsize=10, fontweight="bold", color="white")
    left += v

ax3.set_xlim(0, BUSCO_N)
ax3.set_ylim(-1, 1)
ax3.set_yticks([])
ax3.set_xlabel("Numero de BUSCOs (n = 1.367, insecta_odb10)")
ax3.set_title("C   Completude BUSCO: C:96,2% [S:39,9%,D:56,3%], F:1,9%, M:1,9%",
              loc="left", fontweight="bold", pad=8, fontsize=11)
patches = [plt.Rectangle((0, 0), 1, 1, color=c) for c in BUSCO_COLORS]
ax3.legend(patches, busco_labels, loc="upper center",
           bbox_to_anchor=(0.5, -0.28), frameon=False, ncol=4,
           handlelength=1.1, handletextpad=0.5, columnspacing=1.2)

# --- panel D: TransDecoder ORF type breakdown (donut) -------------------------

orf_labels = list(ORF_TYPES.keys())
orf_vals = list(ORF_TYPES.values())

wedge_props = dict(width=0.48, edgecolor="white", linewidth=1.2)
ax4.pie(orf_vals, colors=ORF_COLORS, startangle=90, counterclock=False,
         wedgeprops=wedge_props)
ax4.text(0, 0, f"{N_PROTEINS:,}\nORFs", ha="center", va="center",
          fontsize=10.5, fontweight="bold", color="#333333", multialignment="center")

legend_labels = [f"{lbl}  {v:,} ({100.0 * v / N_PROTEINS:.1f}%)"
                  for lbl, v in zip(orf_labels, orf_vals)]
patches4 = [plt.Rectangle((0, 0), 1, 1, color=c)
            for c in ORF_COLORS]
ax4.legend(patches4, legend_labels, loc="lower center",
           bbox_to_anchor=(0.5, -0.28), frameon=False, ncol=2,
           handlelength=1.0, handletextpad=0.5, columnspacing=1.0)
ax4.set_title("D   Tipos de ORF preditos (TransDecoder)", loc="left",
              fontweight="bold", pad=8)

# --- save ---------------------------------------------------------------------

outdir = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(outdir, "assembly_qc_summary")

fig.savefig(base + ".png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(base + ".tiff", dpi=300, bbox_inches="tight", facecolor="white")

print("Saved:")
print("  " + base + ".png  (300 dpi)")
print("  " + base + ".tiff (300 dpi)")
