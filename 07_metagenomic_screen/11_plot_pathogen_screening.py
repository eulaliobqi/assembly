#!/usr/bin/env python3
"""
Pathogen screening figure: (A) reconciliation of the 30 original DIAMOND/NR virus
hits into retrotransposon-like elements / mycoviruses / genuine arthropod viruses,
and (B) genome-wide breadth of coverage for the Xylella fastidiosa and Aster
Yellows phytoplasma leads (both refuted).

Exports: pathogen_screening.png (300 dpi) and .tiff (300 dpi)

Data source (verified against files on disk, not re-derived):
  - results/annotation_complete.tsv (is_virus flag, source_organism) + live NCBI
    taxonomy lookup for family classification (session log)
  - 07_metagenomic_screen/results/pathogen_confirmation/idxstats.tsv +
    depth_covered_only.tsv (breadth of coverage, rRNA overlap check)

Usage:
  python 07_metagenomic_screen/11_plot_pathogen_screening.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

# --- data (verified) -----------------------------------------------------------

VIRUS_CATEGORIES = [
    ("Retrotransposon-like\n(Metaviridae + Eupolintoviridae)", 12, "#BDBDBD"),
    ("Micovirus\n(infecta fungos ja detectados)",                4, "#F07D0C"),
    ("Virus genuino de artropode\n(sem precedente fitopatogenico)", 14, "#2C7BB6"),
]
VIRUS_TOTAL = 30
VIRUS_RDRP_CONFIRMED = 4  # of the 14 genuine, confirmed by domain+identity

PATHOGENS = [
    ("Xylella fastidiosa\nsubsp. multiplex\n(NZ_CP136968.1, 2.708.059 pb)", 0.28, 2887, 173394056),
    ("Aster Yellows\nphytoplasma\n(NC_007716.1, 706.569 pb)",              0.17, 28,   173394056),
]

plt.rcParams.update({
    "font.family":       "Arial",
    "font.size":         11,
    "axes.titlesize":    12,
    "axes.labelsize":    11,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "legend.fontsize":   9,
    "axes.linewidth":    0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

fig = plt.figure(figsize=(11, 5.2))
gs = GridSpec(1, 2, figure=fig, wspace=0.42, left=0.09, right=0.97, top=0.80, bottom=0.14)

ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])

# --- panel A: viral census reconciliation --------------------------------------

labels = [c[0] for c in VIRUS_CATEGORIES]
vals = [c[1] for c in VIRUS_CATEGORIES]
colors = [c[2] for c in VIRUS_CATEGORIES]

y = np.arange(len(labels))
ax1.barh(y, vals, height=0.55, color=colors, zorder=3)
for i, v in enumerate(vals):
    ax1.text(v + VIRUS_TOTAL * 0.02, i, f"{v}", va="center", fontsize=11, fontweight="bold")
ax1.set_yticks(y)
ax1.set_yticklabels(labels, fontsize=10)
ax1.set_xlabel("N de hits (dos 30 originais)")
ax1.set_xlim(0, VIRUS_TOTAL * 1.25)
ax1.set_title("A   Reclassificacao dos 30 hits virais\n(anotacao DIAMOND/NR original)",
              loc="left", fontweight="bold", fontsize=11.5, pad=8)
ax1.grid(axis="x", color="#e0e0e0", lw=0.5, zorder=0)
ax1.tick_params(axis="y", length=0)
ax1.text(0, -0.85,
          f"Dos {VIRUS_RDRP_CONFIRMED} virus genuinos confirmados por 2 fontes independentes\n"
          f"(dominio RdRp + identidade BLASTx), nenhum tem precedente de fitopatogenicidade.\n"
          f"Busca dirigida pela familia RdRp de Phytoreovirus: 0 hits.",
          fontsize=8.8, color="#555555", va="top")

# --- panel B: Xylella/phytoplasma genome-wide coverage -------------------------

labels_b = [p[0] for p in PATHOGENS]
breadth = [p[1] for p in PATHOGENS]
reads = [p[2] for p in PATHOGENS]
total_reads = PATHOGENS[0][3]

y2 = np.arange(len(labels_b))
bars = ax2.barh(y2, breadth, height=0.45, color="#D7191C", zorder=3)
for i, (b, r) in enumerate(zip(breadth, reads)):
    pct_reads = 100 * r / total_reads
    ax2.text(b + 0.05, i, f"{b}% da cobertura\n({r:,} reads, {pct_reads:.4f}% do total)",
              va="center", fontsize=9.3, fontweight="bold")
ax2.set_yticks(y2)
ax2.set_yticklabels(labels_b, fontsize=9.7)
ax2.set_xlabel("Amplitude de cobertura genoma-inteira (%)")
ax2.set_xlim(0, 3.2)
ax2.set_title("B   Xylella/fitoplasma: cobertura genoma-inteira\n(mapeamento dos ~173M reads brutos)",
              loc="left", fontweight="bold", fontsize=11.5, pad=8)
ax2.grid(axis="x", color="#e0e0e0", lw=0.5, zorder=0)
ax2.tick_params(axis="y", length=0)
ax2.text(0, -0.85,
          "98,0% (Xylella) e 100% (fitoplasma) das poucas posicoes cobertas\n"
          "caem dentro de operons de rRNA 16S/23S (conferido via GFF3 real) --\n"
          "cross-mapping de regiao conservada, nao presenca real. AMBOS REFUTADOS.",
          fontsize=8.8, color="#555555", va="top")

fig.suptitle("Triagem de patogeno microbiano causador do amarelao (Camada 3) -- nenhum confirmado",
             fontsize=13.5, fontweight="bold", y=0.965)

# --- save ---------------------------------------------------------------------

outdir = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(outdir, "pathogen_screening")

fig.savefig(base + ".png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(base + ".tiff", dpi=300, bbox_inches="tight", facecolor="white")

print("Saved:")
print("  " + base + ".png  (300 dpi)")
print("  " + base + ".tiff (300 dpi)")
