#!/usr/bin/env python3
"""
Full microbiome census figure: Bacteria (540 hits) and Fungi (256 hits) genus-level
breakdown, all hits grouped -- not just the pre-selected candidates from earlier
sessions.

Exports: microbiome_census.png (300 dpi) and .tiff (300 dpi)

Data source (verified against files on disk, not re-derived):
  - results/annotation_complete.tsv (is_bacteria/is_fungi flags, source_organism)
  - 07_metagenomic_screen/results/full_microbiome_census/bacterial_genus_breakdown.tsv
  - 07_metagenomic_screen/results/fungal_breakdown/fungal_genus_breakdown.tsv

Usage:
  python 07_metagenomic_screen/10_plot_microbiome_census.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

# --- data (verified against annotation_complete.tsv + census tables) ----------

BACTERIA_TOTAL = 540
FUNGI_TOTAL = 256

# category, n, group (endosymbiont/plant-origin/generalist/bias-artifact/tested-refuted)
BACTERIA = [
    ("Gammaproteobacteria sp. (nao classif.)", 118, "generalist"),
    ("Herbaspirillum spp.",                     88, "plant"),
    ("Chryseobacterium/Flavobacteriaceae",      71, "generalist"),
    ("Enterobacterales/Enterobacter",           59, "generalist"),
    ("Candidatus Karelsulcia muelleri",         57, "endosymbiont"),
    ("Outros generos singleton",                47, "generalist"),
    ("Klebsiella pneumoniae",                   31, "artifact"),
    ("Acinetobacter spp.",                      20, "generalist"),
    ("Cyanobacteria",                           18, "plant"),
    ("Patogenos humanos/aviarios (vies banco)", 14, "artifact"),
    ("Wolbachia endosymbiont",                   6, "endosymbiont"),
    ("Simbiontes marinhos (impossivel)",         6, "artifact"),
    ("Xylella + Aster Yellows phytoplasma",      2, "refuted"),
    ("Sodalis-like + outros singleton (n=1)",    3, "endosymbiont"),
]

FUNGI = [
    ("Entomophthora muscae",       96, "generalist"),
    ("Metarhizium spp. (6 spp.)",  56, "generalist"),
    ("Neoconidiobolus thromboides",26, "generalist"),
    ("Massospora cicadina",        18, "generalist"),
    ("Erysiphe pulchra (oidio)",   15, "implausible"),
    ("Fusarium spp. (murcha)",      8, "candidate"),
    ("Outros generos singleton",   37, "generalist"),
]

GROUP_COLORS = {
    "endosymbiont":    "#1A9641",   # green -- confirmed mutualist, expected background
    "plant":           "#F07D0C",   # orange -- likely plant-derived (xylem sap)
    "generalist":      "#2C7BB6",   # blue -- not relevant to amarelao (environmental / entomopathogenic)
    "artifact":        "#BDBDBD",   # gray -- likely database-bias / spurious
    "refuted":         "#D7191C",   # red -- directly tested and refuted (Camada 3)
    "implausible":     "#BDBDBD",   # gray -- phytopathogen but mechanistically implausible
    "candidate":       "#F07D0C",   # orange -- only mechanistically plausible phytopathogen lead
}

GROUP_LABELS = {
    "endosymbiont":   "Endossimbionte (confirmado, pano de fundo)",
    "plant":          "Provavel origem vegetal (xilema ingerido)",
    "generalist":     "Nao relevante p/ amarelao (ambiental/entomopatogenico)",
    "artifact":       "Provavel artefato/vies de banco",
    "refuted":        "Testado e REFUTADO (Camada 3)",
    "implausible":    "Fitopatogeno, mecanisticamente improvavel",
    "candidate":      "Unico candidato fitopatogenico plausivel (sinal fraco)",
}

plt.rcParams.update({
    "font.family":       "Arial",
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "xtick.labelsize":   8.5,
    "ytick.labelsize":   8.5,
    "legend.fontsize":   7.5,
    "axes.linewidth":    0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

fig = plt.figure(figsize=(11, 11))
gs = GridSpec(2, 1, figure=fig, height_ratios=[14, 8], hspace=0.32,
              left=0.30, right=0.95, top=0.93, bottom=0.06)

ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])


def plot_panel(ax, data, total, title, subtitle):
    data_sorted = sorted(data, key=lambda x: x[1])
    labels = [d[0] for d in data_sorted]
    vals = [d[1] for d in data_sorted]
    groups = [d[2] for d in data_sorted]
    colors = [GROUP_COLORS[g] for g in groups]

    y = np.arange(len(labels))
    ax.barh(y, vals, height=0.62, color=colors, zorder=3)
    for i, v in enumerate(vals):
        ax.text(v + total * 0.008, i, f"{v}", va="center", fontsize=8, fontweight="bold", color="#222222")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xlabel("N de proteinas (melhor hit DIAMOND)")
    ax.set_xlim(0, max(vals) * 1.18)
    ax.set_title(f"{title}\n{subtitle}", loc="left", fontweight="bold", fontsize=11, pad=10)
    ax.grid(axis="x", color="#e0e0e0", lw=0.5, zorder=0)
    ax.tick_params(axis="y", length=0)

    present_groups = list(dict.fromkeys(groups))
    patches = [plt.Rectangle((0, 0), 1, 1, color=GROUP_COLORS[g]) for g in present_groups]
    legend_labels = [GROUP_LABELS[g] for g in present_groups]
    ax.legend(patches, legend_labels, loc="lower right", frameon=False,
              fontsize=7.3, handlelength=1.0, handletextpad=0.5)


plot_panel(ax1, BACTERIA, BACTERIA_TOTAL,
           "A   Censo completo de Bacteria (540 hits, todos os generos)",
           f"Total: {BACTERIA_TOTAL} proteinas -- nao apenas os ~60 candidatos ja pre-selecionados em sessoes anteriores")

plot_panel(ax2, FUNGI, FUNGI_TOTAL,
           "B   Censo completo de Fungi (256 hits, todos os generos)",
           f"Total: {FUNGI_TOTAL} proteinas -- 77% (196) sao entomopatogenicos, irrelevantes para o amarelao")

fig.suptitle("Censo completo do microbioma bacteriano e fungico (Camada 3)", fontsize=13, fontweight="bold", y=0.985)

# --- save ---------------------------------------------------------------------

outdir = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(outdir, "microbiome_census")

fig.savefig(base + ".png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(base + ".tiff", dpi=300, bbox_inches="tight", facecolor="white")

print("Saved:")
print("  " + base + ".png  (300 dpi)")
print("  " + base + ".tiff (300 dpi)")
