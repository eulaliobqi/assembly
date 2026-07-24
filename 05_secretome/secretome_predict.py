#!/usr/bin/env python3
"""
secretome_predict.py
Secretome prediction for Mahanarva spectabilis salivary gland proteins.

Workflow:
  Phase 1: validate   - check tools and input files
  Phase 2: prepare    - clean FASTA headers and remove stop codons
  Phase 3: tmbed      - predict signal peptide + transmembrane segments (TMbed)
  Phase 5: filter     - classical secretome (SP present AND TM <= 1)
  Phase 6: annotate   - merge with annotation_complete.tsv
  Phase 7: save       - write TSV output files
  Phase 8: report     - text summary
  Phase 9: figures    - 3-panel publication figure

SignalP6/TMHMM were replaced by TMbed (Bernhofer & Rost 2022, BMC
Bioinformatics): both require a DTU academic license/manual tarball
download that was never completed in this or two other lab projects
(see README Known Issues). TMbed is pip-installable, runs fully local
(no login/license), and predicts signal peptide + TM helix/strand in a
single protein-language-model pass.

Usage:
  cd /home/eulalio/trinity_maharnava
  conda activate secretome
  python 05_secretome/secretome_predict.py

  # Skip TMbed if already run:
  python 05_secretome/secretome_predict.py --resume
"""

import argparse
import csv
import logging
import subprocess
import sys
from collections import Counter
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE       = Path(__file__).resolve().parent.parent
INPUT_PEP  = BASE / "data" / "transdecoder" / "trinity_nr95.fasta.transdecoder.pep"
ANNOTATION = BASE / "results" / "annotation_complete.tsv"
OUT_DIR    = BASE / "results" / "secretome"
FIG_DIR    = BASE / "figures"
CLEAN_PEP  = OUT_DIR / "proteins_clean.fa"

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Shell helper ──────────────────────────────────────────────────────────────
def run(cmd, check=True):
    """Run shell command, log stderr on failure."""
    log.info("CMD: %s", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        log.error("STDERR:\n%s", r.stderr[-3000:])
        raise RuntimeError(f"Command failed (rc={r.returncode}): {cmd}")
    return r.stdout, r.stderr, r.returncode


# =============================================================================
# Phase 1: Validate
# =============================================================================
def validate(resume):
    log.info("=== Phase 1: Validate inputs and tools ===")

    if not INPUT_PEP.exists():
        sys.exit(f"[ERROR] Input not found: {INPUT_PEP}")
    if not ANNOTATION.exists():
        log.warning("Annotation file not found: %s  (will skip merge)", ANNOTATION)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    check = subprocess.run(
        [sys.executable, "-m", "tmbed", "--help"],
        capture_output=True, text=True,
    )
    if check.returncode != 0:
        sys.exit(
            "[ERROR] tmbed module not importable in this environment.\n"
            "Install: pip install git+https://github.com/BernhoferM/TMbed.git\n"
            "(see environment/env_secretome.yml)"
        )
    log.info("TMbed found: %s -m tmbed", sys.executable)

    return {}


# =============================================================================
# Phase 2: Prepare FASTA
# =============================================================================
def prepare_fasta():
    """
    Strip multi-word headers to first token, remove stop codons (*),
    skip sequences shorter than 10 aa (too short for signal peptide).
    """
    log.info("=== Phase 2: Prepare clean FASTA ===")

    if CLEAN_PEP.exists():
        # Count existing records to return n_total
        n = sum(1 for line in open(CLEAN_PEP) if line.startswith(">"))
        log.info("Clean FASTA exists (%d seqs), skipping.", n)
        return n

    records = []
    header = None
    seq_lines = []

    with open(INPUT_PEP) as fh:
        for line in fh:
            line = line.rstrip()
            if line.startswith(">"):
                if header is not None:
                    seq = "".join(seq_lines).replace("*", "")
                    if len(seq) >= 10:
                        records.append((header, seq))
                header = line[1:].split()[0]
                seq_lines = []
            else:
                seq_lines.append(line)
        if header is not None:
            seq = "".join(seq_lines).replace("*", "")
            if len(seq) >= 10:
                records.append((header, seq))

    with open(CLEAN_PEP, "w") as out:
        for hdr, seq in records:
            out.write(f">{hdr}\n{seq}\n")

    log.info("Wrote %d sequences to %s", len(records), CLEAN_PEP)
    return len(records)


# =============================================================================
# Phase 3: TMbed prediction (signal peptide + transmembrane, single model)
# =============================================================================
def run_tmbed(resume):
    log.info("=== Phase 3: TMbed prediction (signal peptide + TM) ===")

    pred_file = OUT_DIR / "tmbed_results.pred"

    if pred_file.exists() and resume:
        log.info("TMbed output found, using cached results.")
    else:
        cmd = (
            f"{sys.executable} -m tmbed predict "
            f"-f {CLEAN_PEP} -p {pred_file} --out-format=2"
        )
        run(cmd)

    sp_data, tm_data = parse_tmbed(pred_file)
    return sp_data, tm_data


def parse_tmbed(result_file):
    """
    Parse TMbed --out-format=2 (tabular, directed segments):
      >protein_id
      AA  PRD  P(B)  P(H)  P(S)  P(i)  P(o)
      <one row per residue>
      <blank line before next record>

    Per-residue label alphabet (directed): B/b (TM beta strand),
    H/h (TM alpha helix), S (signal peptide), .  (other/globular).
    A contiguous run of the same TM letter (H/h or B/b) = one helix/strand
    segment; classical secretome = has_sp AND tm_count <= 1 (same
    definition previously used for SignalP+TMHMM).
    """
    if not result_file.exists():
        sys.exit(f"[ERROR] TMbed output not found: {result_file}")

    sp_data, tm_data = {}, {}
    prot_id = None
    labels, sp_probs = [], []

    def flush():
        if prot_id is None:
            return
        has_sp = "S" in labels
        sp_len = 0
        for lab in labels:
            if lab != "S":
                break
            sp_len += 1
        sp_prob = round(max(sp_probs[:sp_len]) if has_sp else (max(sp_probs) if sp_probs else 0.0), 4)

        tm_runs = []
        prev_lab = None
        for lab in labels:
            if lab in ("H", "h", "B", "b"):
                if lab != prev_lab:
                    tm_runs.append(lab)
                prev_lab = lab
            else:
                prev_lab = None
        tm_count = len(tm_runs)

        sp_data[prot_id] = {
            "has_sp": has_sp,
            "sp_prob": sp_prob,
            "cs_pos": str(sp_len) if has_sp else "",
            "signalp_pred": "SP(Sec/SPI)" if has_sp else "OTHER",
        }
        tm_data[prot_id] = {"tm_count": tm_count, "topology": ",".join(tm_runs)}

    with open(result_file) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith(">"):
                flush()
                prot_id = line[1:].split()[0]
                labels, sp_probs = [], []
                continue
            parts = line.split()
            if not parts or parts[0] == "AA":
                continue
            # AA  PRD  P(B)  P(H)  P(S)  P(i)  P(o)
            if len(parts) < 5:
                continue
            labels.append(parts[1])
            try:
                sp_probs.append(float(parts[4]))
            except ValueError:
                sp_probs.append(0.0)
        flush()

    n_sp = sum(1 for v in sp_data.values() if v["has_sp"])
    n_tm = sum(1 for v in tm_data.values() if v["tm_count"] > 0)
    log.info("TMbed: %d proteins parsed, %d with signal peptide, %d with TM segments",
              len(sp_data), n_sp, n_tm)
    return sp_data, tm_data


# =============================================================================
# Phase 5: Filter classical secretome
# =============================================================================
def filter_secretome(sp_data, tm_data, n_total):
    log.info("=== Phase 5: Filter classical secretome ===")
    log.info("Criteria: signal peptide = SP(Sec/SPI)  AND  TM helices <= 1")

    all_ids = set(sp_data) | set(tm_data)

    results = []
    for pid in all_ids:
        sp = sp_data.get(pid, {
            "has_sp": False, "sp_prob": 0.0,
            "cs_pos": "", "signalp_pred": "OTHER"
        })
        tm = tm_data.get(pid, {"tm_count": 0, "topology": ""})

        is_secreted = sp["has_sp"] and (tm["tm_count"] <= 1)

        results.append({
            "protein_id":     pid,
            "is_secreted":    is_secreted,
            "has_sp":         sp["has_sp"],
            "sp_prob":        round(sp["sp_prob"], 4),
            "cs_pos":         sp.get("cs_pos", ""),
            "signalp_pred":   sp.get("signalp_pred", "OTHER"),
            "tm_count":       tm["tm_count"],
            "topology":       tm.get("topology", ""),
        })

    sp_pos   = [r for r in results if r["has_sp"]]
    secreted = [r for r in results if r["is_secreted"]]
    excluded = [r for r in results if r["has_sp"] and not r["is_secreted"]]

    log.info("Total proteins:      %d", n_total)
    log.info("Signal peptide (+):  %d  (%.1f%%)", len(sp_pos),  100 * len(sp_pos)  / n_total)
    log.info("Classical secretome: %d  (%.1f%%)", len(secreted), 100 * len(secreted) / n_total)
    log.info("  SP + TM > 1 (excl): %d", len(excluded))

    return results, secreted


# =============================================================================
# Phase 6: Merge with functional annotation
# =============================================================================
def merge_annotation(results):
    log.info("=== Phase 6: Merge with functional annotation ===")

    annot = {}
    if ANNOTATION.exists():
        with open(ANNOTATION, newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            for row in reader:
                pid = row.get("protein_id", "").strip()
                if pid:
                    annot[pid] = row
        log.info("Loaded annotation for %d proteins", len(annot))
    else:
        log.warning("Annotation file not found; annotation columns will be empty.")

    merged = []
    for r in results:
        pid = r["protein_id"]
        a   = annot.get(pid, {})
        merged.append({
            **r,
            "diamond_subject":  a.get("diamond_subject", ""),
            "gene_name":        a.get("gene_name", ""),
            "diamond_pident":   a.get("diamond_pident", ""),
            "diamond_evalue":   a.get("diamond_evalue", ""),
            "source_organism":  a.get("source_organism", ""),
            "eggnog_desc":      a.get("eggnog_desc", ""),
            "go_terms":         a.get("go_terms", ""),
            "kegg_ko":          a.get("kegg_ko", ""),
            "kegg_pathway":     a.get("kegg_pathway", ""),
            "cog_category":     a.get("cog_category", ""),
            "pfam_domains":     a.get("pfam_domains", ""),
        })

    return merged


# =============================================================================
# Phase 7: Save outputs
# =============================================================================
FIELDS = [
    "protein_id", "is_secreted", "has_sp", "sp_prob", "cs_pos",
    "signalp_pred", "tm_count", "topology",
    "diamond_subject", "gene_name", "diamond_pident", "diamond_evalue",
    "source_organism", "eggnog_desc", "go_terms",
    "kegg_ko", "kegg_pathway", "cog_category", "pfam_domains",
]


def save_outputs(merged):
    log.info("=== Phase 7: Save TSV outputs ===")

    secreted_rows = [r for r in merged if r["is_secreted"]]

    # All proteins with SP/TM predictions + annotation
    all_out = OUT_DIR / "secretome_all.tsv"
    with open(all_out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(merged)

    # Secretome only
    sec_out = OUT_DIR / "secretome_classical.tsv"
    with open(sec_out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(secreted_rows)

    log.info("All predictions: %s  (%d rows)", all_out, len(merged))
    log.info("Classical secretome: %s  (%d proteins)", sec_out, len(secreted_rows))
    return secreted_rows


# =============================================================================
# Phase 8: Report
# =============================================================================
COG_NAMES = {
    "J": "Translation, ribosomal structure",
    "K": "Transcription",
    "L": "Replication, recombination, repair",
    "D": "Cell cycle control, division",
    "V": "Defense mechanisms",
    "T": "Signal transduction",
    "M": "Cell wall/membrane biogenesis",
    "N": "Cell motility",
    "U": "Intracellular trafficking, secretion",
    "O": "Post-translational modification, chaperones",
    "C": "Energy production and conversion",
    "G": "Carbohydrate transport and metabolism",
    "E": "Amino acid transport and metabolism",
    "F": "Nucleotide transport and metabolism",
    "H": "Coenzyme transport and metabolism",
    "I": "Lipid transport and metabolism",
    "P": "Inorganic ion transport and metabolism",
    "Q": "Secondary metabolites biosynthesis",
    "R": "General function prediction only",
    "S": "Function unknown",
}


def generate_report(merged, n_total):
    log.info("=== Phase 8: Generate report ===")

    secreted = [r for r in merged if r["is_secreted"]]
    sp_pos   = [r for r in merged if r["has_sp"]]

    n_sec = len(secreted)
    n_sp  = len(sp_pos)

    def pct(n, d):
        return 100 * n / d if d > 0 else 0.0

    annotated = sum(1 for r in secreted if r["diamond_subject"])
    go_ann    = sum(1 for r in secreted if r["go_terms"])
    kegg_ann  = sum(1 for r in secreted if r["kegg_ko"])
    pfam_ann  = sum(1 for r in secreted if r["pfam_domains"])

    cog_c = Counter()
    for r in secreted:
        cog = r.get("cog_category", "")
        if cog and cog not in ("", "-"):
            for c in cog:
                if c.strip():
                    cog_c[c.strip()] += 1

    lines = [
        "=" * 62,
        "SECRETOME PREDICTION REPORT",
        "Mahanarva spectabilis - salivary gland proteins",
        "=" * 62,
        "",
        "PIPELINE",
        "  TMbed (Bernhofer & Rost 2022) - signal peptide + TM segment",
        "  prediction in a single protein-language-model pass",
        "  (replaces SignalP+TMHMM, blocked by DTU academic license)",
        "  Filter: signal peptide present  AND  TM segments <= 1",
        "",
        "RESULTS",
        "-" * 42,
        f"  Total proteins analyzed :  {n_total:>7,}",
        f"  Signal peptide (SP+)    :  {n_sp:>7,}  ({pct(n_sp, n_total):.1f}%)",
        f"  TM helix only (excl.)   :  {n_sp - n_sec:>7,}",
        f"  Classical secretome     :  {n_sec:>7,}  ({pct(n_sec, n_total):.1f}%)",
        "",
        "ANNOTATION OF CLASSICAL SECRETOME",
        "-" * 42,
        f"  DIAMOND annotated       :  {annotated:>7,}  ({pct(annotated, n_sec):.1f}%)",
        f"  With GO terms           :  {go_ann:>7,}  ({pct(go_ann, n_sec):.1f}%)",
        f"  With KEGG KO            :  {kegg_ann:>7,}  ({pct(kegg_ann, n_sec):.1f}%)",
        f"  With Pfam domains       :  {pfam_ann:>7,}  ({pct(pfam_ann, n_sec):.1f}%)",
        "",
        "TOP COG CATEGORIES (classical secretome)",
        "-" * 42,
    ]

    for cat, cnt in cog_c.most_common(10):
        name = COG_NAMES.get(cat, "Unknown")
        lines.append(f"  [{cat}] {name:<42} {cnt:>5}")

    lines += ["", "=" * 62]

    report_text = "\n".join(lines)
    report_path = OUT_DIR / "secretome_report.txt"
    with open(report_path, "w") as fh:
        fh.write(report_text)

    print("\n" + report_text + "\n")
    log.info("Report saved: %s", report_path)

    return {
        "n_total": n_total, "n_sp": n_sp, "n_sec": n_sec,
        "annotated": annotated, "go_ann": go_ann,
        "kegg_ann": kegg_ann, "pfam_ann": pfam_ann,
    }


# =============================================================================
# Phase 9: Figures
# =============================================================================
def generate_figures(merged, stats):
    log.info("=== Phase 9: Generate publication figures ===")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
        import numpy as np
    except ImportError:
        log.warning("matplotlib not available; skipping figures.")
        return

    # ── Font setup ────────────────────────────────────────────────────────────
    from matplotlib import font_manager
    arial_found = any("Arial" in f.name for f in font_manager.fontManager.ttflist)
    font_family = "Arial" if arial_found else "DejaVu Sans"

    plt.rcParams.update({
        "font.family":        font_family,
        "font.size":          10,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "figure.facecolor":   "white",
        "axes.facecolor":     "white",
    })

    n_total = stats["n_total"]
    n_sp    = stats["n_sp"]
    n_sec   = stats["n_sec"]

    # Color palette (consistent with project figures)
    C_BLUE   = "#4C72B0"
    C_ORANGE = "#DD8452"
    C_GREEN  = "#55A868"
    C_RED    = "#C44E52"

    # ── Build figure: 3 panels ─────────────────────────────────────────────
    fig = plt.figure(figsize=(15, 6))
    gs  = gridspec.GridSpec(
        1, 3,
        figure=fig,
        wspace=0.38,
        left=0.06, right=0.97,
        top=0.90, bottom=0.13,
    )

    # ── Panel A: Secretome funnel (horizontal bars) ────────────────────────
    ax_a = fig.add_subplot(gs[0])

    steps  = [n_total, n_sp, n_sec]
    labels = [
        f"All proteins\n(n = {n_total:,})",
        f"Signal peptide (+)\n(n = {n_sp:,})",
        f"Classical secretome\n(n = {n_sec:,})",
    ]
    colors = [C_BLUE, C_ORANGE, C_GREEN]
    y_pos  = [2, 1, 0]
    max_v  = n_total

    for y, val, lbl, col in zip(y_pos, steps, labels, colors):
        ax_a.barh(
            y, val, height=0.52,
            color=col, alpha=0.88,
            edgecolor="white", linewidth=1.5,
        )
        pct = 100 * val / max_v
        ax_a.text(
            val + max_v * 0.013, y,
            f"{val:,}  ({pct:.1f}%)",
            va="center", ha="left", fontsize=9, color="#333333",
        )

    ax_a.set_yticks(y_pos)
    ax_a.set_yticklabels(labels, fontsize=9.5)
    ax_a.set_xlabel("Number of proteins", fontsize=10)
    ax_a.set_xlim(0, max_v * 1.38)
    ax_a.set_title("A  Secretome prediction funnel",
                   fontsize=11, fontweight="bold", loc="left", pad=8)
    ax_a.spines["left"].set_visible(False)
    ax_a.tick_params(axis="y", length=0)

    # ── Panel B: TM helix distribution (SP+ proteins) ─────────────────────
    ax_b = fig.add_subplot(gs[1])

    sp_rows   = [r for r in merged if r["has_sp"]]
    tm_sec    = [r["tm_count"] for r in sp_rows if r["is_secreted"]]
    tm_excl   = [r["tm_count"] for r in sp_rows if not r["is_secreted"]]

    all_tm_vals = tm_sec + tm_excl
    max_tm = max(all_tm_vals) if all_tm_vals else 5
    bins   = list(range(0, min(max_tm + 2, 12)))

    ax_b.hist(
        tm_sec, bins=bins, alpha=0.82, color=C_GREEN,
        label=f"Secretome  (n = {len(tm_sec):,})",
        align="left", edgecolor="white", linewidth=0.7,
    )
    ax_b.hist(
        tm_excl, bins=bins, alpha=0.72, color=C_RED,
        label=f"Excluded (TM > 1)  (n = {len(tm_excl):,})",
        align="left", edgecolor="white", linewidth=0.7,
    )
    ax_b.axvline(
        x=1.5, color="#555555", linestyle="--",
        linewidth=1.2, alpha=0.75, label="Cutoff (TM = 1)",
    )

    ax_b.set_xlabel("Predicted TM helices", fontsize=10)
    ax_b.set_ylabel("Number of proteins",   fontsize=10)
    ax_b.set_title("B  TM helix distribution\n(signal peptide-positive only)",
                   fontsize=11, fontweight="bold", loc="left", pad=8)
    ax_b.legend(fontsize=8.5, frameon=False, loc="upper right")
    ax_b.set_xticks(bins[:-1])

    # ── Panel C: COG categories donut (classical secretome) ───────────────
    ax_c = fig.add_subplot(gs[2])

    secreted = [r for r in merged if r["is_secreted"]]
    cog_c    = Counter()
    for r in secreted:
        cog = r.get("cog_category", "")
        if cog and cog not in ("", "-"):
            for c in cog:
                if c.strip():
                    cog_c[c.strip()] += 1

    COG_SHORT = {
        "J": "Translation",        "K": "Transcription",
        "L": "Replication/repair", "D": "Cell division",
        "V": "Defense",            "T": "Signal transd.",
        "M": "Cell membrane",      "N": "Motility",
        "U": "Trafficking/secret.","O": "Chaperones",
        "C": "Energy",             "G": "Carbohydrate metab.",
        "E": "Amino acid metab.",  "F": "Nucleotide metab.",
        "H": "Coenzyme metab.",    "I": "Lipid metab.",
        "P": "Ion transport",      "Q": "Sec. metabolites",
        "R": "Gen. function",      "S": "Unknown",
    }

    if cog_c:
        top8     = cog_c.most_common(8)
        other_n  = sum(v for k, v in cog_c.items() if k not in dict(top8))
        pie_lbls = [f"[{c}] {COG_SHORT.get(c, c)}" for c, _ in top8]
        pie_vals = [cnt for _, cnt in top8]
        if other_n > 0:
            pie_lbls.append("Other")
            pie_vals.append(other_n)

        cmap   = plt.get_cmap("tab10")
        colors_pie = [cmap(i / len(pie_vals)) for i in range(len(pie_vals))]

        wedges, _ = ax_c.pie(
            pie_vals,
            colors=colors_pie,
            wedgeprops={"width": 0.48, "edgecolor": "white", "linewidth": 1.5},
            startangle=90,
        )

        ax_c.legend(
            wedges, pie_lbls,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.06),
            ncol=2,
            fontsize=7.5,
            frameon=False,
            handlelength=0.9,
            handleheight=0.9,
            columnspacing=0.8,
        )
    else:
        ax_c.text(
            0.5, 0.5,
            "No COG data\nfor secretome",
            ha="center", va="center",
            transform=ax_c.transAxes, fontsize=10,
        )
        ax_c.axis("off")

    ax_c.set_title("C  COG functional categories\n(classical secretome)",
                   fontsize=11, fontweight="bold", loc="left", pad=8)

    # ── Save ─────────────────────────────────────────────────────────────────
    for ext, dpi in [("png", 300), ("tiff", 300)]:
        out_path = FIG_DIR / f"secretome_summary.{ext}"
        fig.savefig(
            str(out_path), dpi=dpi,
            bbox_inches="tight", facecolor="white", format=ext,
        )
        log.info("Saved: %s", out_path)

    plt.close(fig)
    log.info("Figures written to %s", FIG_DIR)


# =============================================================================
# Main
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Secretome prediction - Mahanarva spectabilis salivary gland"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Skip TMbed if output files already exist",
    )
    args = parser.parse_args()

    log.info("Secretome prediction pipeline - Mahanarva spectabilis")
    log.info("Project root: %s", BASE)

    validate(args.resume)
    n_total = prepare_fasta()
    sp_data, tm_data = run_tmbed(args.resume)

    all_results, secreted = filter_secretome(sp_data, tm_data, n_total)

    merged = merge_annotation(all_results)
    save_outputs(merged)
    stats  = generate_report(merged, n_total)
    generate_figures(merged, stats)

    log.info("=== DONE ===")
    log.info("Outputs  : %s", OUT_DIR)
    log.info("Figures  : %s", FIG_DIR)


if __name__ == "__main__":
    main()
