#!/usr/bin/env python3
"""
GroEL maximum-likelihood phylogeny figure (Sulcia/Karelsulcia references + Sodalis/
Bacteroides fragilis outgroup + the M. spectabilis candidate). Renders the tree
AS COMPUTED -- the candidate does NOT nest within the Sulcia clade with adequate
bootstrap support (49-72%, below the 95% threshold set as the success criterion),
and this figure shows that plainly rather than a cleaned-up/reassuring version.

Exports: groel_phylogeny.png (300 dpi) and .tiff (300 dpi)

Data source (verified against file on disk, not re-derived):
  - 08_metagenomic_deep/results/phylogenetics/groel_tree_v2.contree (IQ-TREE
    ultrafast-bootstrap consensus tree, real run output, not re-fit here)

Usage:
  python 08_metagenomic_deep/02_plot_groel_phylogeny.py
"""

import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from Bio import Phylo
import io

HERE = os.path.dirname(os.path.abspath(__file__))
TREE_FILE = os.path.join(HERE, "results", "phylogenetics", "groel_tree_v2.contree")

TIP_LABELS = {
    "sp|A8Z640.1|CH60_KARMG":  "Ca. Karelsulcia muelleri (ref. GWSS, A8Z640)",
    "YCR11451.1":              "Ca. Karelsulcia muelleri (MAG, YCR11451)",
    "YCJ95658.1":              "Ca. Karelsulcia muelleri (MAG, YCJ95658)",
    "sp|P0C193.1|CH60_SODGL":  "Sodalis glossinidius (P0C193)",
    "sp|Q2NW94.1|CH60_SODGM":  "Sodalis glossinidius (Q2NW94)",
    "WP_005789739.1":          "Bacteroides sp. (outgroup, WP_005789739)",
    "TRINITY_DN26541_c0_g1_i1.p1": "M. spectabilis candidate (este trabalho)",
}

TIP_COLORS = {
    "sp|A8Z640.1|CH60_KARMG":  "#1A9641",
    "YCR11451.1":              "#1A9641",
    "YCJ95658.1":              "#1A9641",
    "sp|P0C193.1|CH60_SODGL":  "#2C7BB6",
    "sp|Q2NW94.1|CH60_SODGM":  "#2C7BB6",
    "WP_005789739.1":          "#BDBDBD",
    "TRINITY_DN26541_c0_g1_i1.p1": "#D7191C",
}

plt.rcParams.update({
    "font.family":  "Arial",
    "font.size":    10,
    "axes.linewidth": 0.8,
})

with open(TREE_FILE) as f:
    newick = f.read()

tree = Phylo.read(io.StringIO(newick), "newick")

# collect bootstrap (confidence) values already parsed by Biopython onto internal nodes
for clade in tree.get_nonterminals():
    if clade.confidence is not None:
        clade._bs_label = f"{int(clade.confidence)}"
    else:
        clade._bs_label = ""

fig, ax = plt.subplots(figsize=(9, 5.6))
fig.subplots_adjust(left=0.06, right=0.97, top=0.80, bottom=0.11)

Phylo.draw(tree, do_show=False, axes=ax,
           label_func=lambda c: TIP_LABELS.get(c.name, "") if c.is_terminal() else "",
           branch_labels=lambda c: c._bs_label if not c.is_terminal() else "")

n_tips = tree.count_terminals()
ax.set_ylim(n_tips + 0.6, 0.4)

# recolor tip labels + tip points according to group
for text in ax.texts:
    for key, label in TIP_LABELS.items():
        if text.get_text().strip() == label:
            text.set_color(TIP_COLORS[key])
            text.set_fontweight("bold" if key.startswith("TRINITY") else "normal")
            text.set_fontsize(9.5)

ax.set_xlabel("Distancia (substituicoes/sitio)")
ax.set_ylabel("")
ax.set_yticks([])
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)

ax.set_title(
    "Filogenia de maxima verossimilhanca (GroEL) -- RESULTADO INCONCLUSIVO\n"
    "Candidato de M. spectabilis nao se agrupa no clado Karelsulcia com suporte adequado "
    "(bootstrap 49-72%, abaixo do criterio de 95%)",
    loc="left", fontweight="bold", fontsize=10.5, pad=14)

legend_items = [
    ("Ca. Karelsulcia muelleri (referencias)", "#1A9641"),
    ("Sodalis glossinidius", "#2C7BB6"),
    ("Bacteroides sp. (outgroup)", "#BDBDBD"),
    ("Candidato M. spectabilis (este trabalho)", "#D7191C"),
]
patches = [plt.Line2D([0], [0], color=c, lw=3) for _, c in legend_items]
labels = [l for l, _ in legend_items]
ax.legend(patches, labels, loc="lower right", frameon=False, fontsize=8)

ax.text(0, -0.14, "Numeros nos ramos = suporte de bootstrap ultrarrapido (IQ-TREE, 1000 replicas)",
        transform=ax.transAxes, fontsize=7.8, color="#555555")

# --- save ---------------------------------------------------------------------

outdir = os.path.join(HERE, "results", "phylogenetics")
base = os.path.join(outdir, "groel_phylogeny")

fig.savefig(base + ".png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(base + ".tiff", dpi=300, bbox_inches="tight", facecolor="white")

print("Saved:")
print("  " + base + ".png  (300 dpi)")
print("  " + base + ".tiff (300 dpi)")
