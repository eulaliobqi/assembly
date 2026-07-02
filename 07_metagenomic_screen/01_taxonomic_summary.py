#!/usr/bin/env python3
"""
Module 4, layer 1 - taxonomic summary and endosymbiont candidate extraction
from the already-existing DIAMOND/eggNOG/taxonkit annotation (no new tool
required; no raw FASTQ needed since only the assembled contigs/proteins are
used downstream).

Rationale (see project README / literature review): spittlebugs (Cercopidae,
same superfamily as Mahanarva spectabilis) are known to carry obligate
nutritional endosymbionts, classically Candidatus Sulcia muelleri plus a
co-symbiont (Zinderia insecticola or, in some lineages, a Sodalis-like
replacement) -- McCutcheon & Moran 2007; Bennett & Moran 2013; Koga & Moran
2014; Foieri et al. 2022 (confirmed Sulcia by 16S in three South American
spittlebug pests closely related to Mahanarva). Contamination of salivary
gland RNA-seq libraries by hemolymph/fat-body-resident symbiont transcripts
is expected and reported elsewhere (e.g. Bansal et al. 2014 for aphid
Buchnera). Xylella fastidiosa and phytoplasma hits are flagged separately and
explicitly deprioritized: phytoplasmas are phloem-limited and Cercopidae are
strict xylem feeders (Backus et al. 2005), so a phytoplasma hit is very
unlikely to be biologically real; Xylella is at least mechanistically
plausible (xylem-limited pathogen, xylem-feeding vector) but has no published
precedent in the genus Mahanarva -- treated as an exploratory lead only.

Usage:
  python 01_taxonomic_summary.py
"""

import re
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RESULTS = BASE / "results"
EXPRESSION = BASE / "expression"
OUTDIR = RESULTS / "endosymbiont_candidates"

ANNOTATION_TSV = RESULTS / "annotation_complete.tsv"
SALMON_SF = EXPRESSION / "salmon-quant.sf"

SYMBIONT_PATTERNS = {
    "Sulcia": re.compile(r"sulcia", re.I),
    "Zinderia": re.compile(r"zinderia", re.I),
    "Sodalis": re.compile(r"sodalis", re.I),
}
LOW_PRIORITY_PATTERNS = {
    "Xylella": re.compile(r"xylella", re.I),
    "Phytoplasma": re.compile(r"phytoplasma", re.I),
}

TRANSCRIPT_SUFFIX_RE = re.compile(r"\.p\d+$")


def protein_to_transcript(protein_id):
    return TRANSCRIPT_SUFFIX_RE.sub("", protein_id)


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    print("Reading %s ..." % ANNOTATION_TSV)
    annot = pd.read_csv(ANNOTATION_TSV, sep="\t", dtype=str, keep_default_na=False)

    print("Reading %s ..." % SALMON_SF)
    salmon = pd.read_csv(SALMON_SF, sep="\t", dtype={"Name": str})
    tpm_by_transcript = dict(zip(salmon["Name"], salmon["TPM"]))

    annot["transcript_id"] = annot["protein_id"].map(protein_to_transcript)
    annot["TPM"] = annot["transcript_id"].map(tpm_by_transcript).fillna(0.0)

    # --- overall taxonomic distribution (versioned, reproducible) ---------
    total = len(annot)
    tax_counts = {
        "Eukaryota": int(annot["is_eukaryote"].astype(int).sum()),
        "Bacteria": int(annot["is_bacteria"].astype(int).sum()),
        "Fungi": int(annot["is_fungi"].astype(int).sum()),
        "Viruses": int(annot["is_virus"].astype(int).sum()),
    }
    none_flagged = annot[
        (annot["is_eukaryote"].astype(int) == 0)
        & (annot["is_bacteria"].astype(int) == 0)
        & (annot["is_fungi"].astype(int) == 0)
        & (annot["is_virus"].astype(int) == 0)
    ]
    tax_counts["Unclassified"] = len(none_flagged)

    summary_lines = [
        "=" * 60,
        "  Taxonomic distribution of best DIAMOND hits (%d proteins)" % total,
        "=" * 60,
    ]
    for k, v in tax_counts.items():
        summary_lines.append("  %-14s: %6d  (%.1f%%)" % (k, v, 100.0 * v / total))
    summary_lines.append("")
    summary_lines.append(
        "  Note: is_eukaryote/is_fungi are independent flags (not mutually"
        " exclusive) -- a fungal hit is also a eukaryote hit by definition."
    )
    summary_lines.append("=" * 60)

    # --- endosymbiont candidates (Sulcia / Zinderia / Sodalis-like) -------
    rows = []
    for label, pattern in SYMBIONT_PATTERNS.items():
        mask = (
            annot["diamond_title"].str.contains(pattern, na=False)
            | annot["source_organism"].str.contains(pattern, na=False)
            | annot["lineage"].str.contains(pattern, na=False)
        )
        hits = annot[mask].copy()
        hits["symbiont_candidate"] = label
        rows.append(hits)

    symbiont_hits = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    symbiont_cols = [
        "symbiont_candidate", "protein_id", "transcript_id", "TPM",
        "diamond_subject", "diamond_pident", "diamond_evalue",
        "source_organism", "pfam_domains", "diamond_title",
    ]
    symbiont_hits = symbiont_hits[symbiont_cols].sort_values(
        ["symbiont_candidate", "TPM"], ascending=[True, False]
    )
    symbiont_out = OUTDIR / "sulcia_sodalis_hits.tsv"
    symbiont_hits.to_csv(symbiont_out, sep="\t", index=False)

    summary_lines.append("")
    summary_lines.append(
        "  Endosymbiont candidates (Sulcia/Zinderia/Sodalis-like): %d proteins"
        % len(symbiont_hits)
    )
    for label in SYMBIONT_PATTERNS:
        n = (symbiont_hits["symbiont_candidate"] == label).sum()
        summary_lines.append("    %-10s: %d" % (label, n))
    summary_lines.append(
        "  -> see %s" % symbiont_out.relative_to(BASE)
    )

    # --- low-priority / exploratory leads (Xylella, phytoplasma) ----------
    low_rows = []
    for label, pattern in LOW_PRIORITY_PATTERNS.items():
        mask = (
            annot["diamond_title"].str.contains(pattern, na=False)
            | annot["source_organism"].str.contains(pattern, na=False)
            | annot["lineage"].str.contains(pattern, na=False)
        )
        hits = annot[mask].copy()
        hits["candidate_pathogen"] = label
        low_rows.append(hits)

    low_hits = pd.concat(low_rows, ignore_index=True) if low_rows else pd.DataFrame()
    if len(low_hits):
        low_cols = [
            "candidate_pathogen", "protein_id", "transcript_id", "TPM",
            "diamond_subject", "diamond_pident", "diamond_evalue",
            "source_organism", "diamond_title",
        ]
        low_hits = low_hits[low_cols]
        low_out = OUTDIR / "low_priority_pathogen_leads.tsv"
        low_hits.to_csv(low_out, sep="\t", index=False)
        summary_lines.append("")
        summary_lines.append(
            "  Low-priority pathogen leads (Xylella/phytoplasma): %d hit(s)"
            " -- exploratory only, single-hit noise likely for phytoplasma"
            " given the xylem-feeding habit of Cercopidae." % len(low_hits)
        )
        summary_lines.append("  -> see %s" % low_out.relative_to(BASE))

    summary_lines.append("=" * 60)
    report = "\n".join(summary_lines)
    print(report)

    report_out = OUTDIR / "taxonomic_summary_report.txt"
    report_out.write_text(report + "\n", encoding="utf-8")
    print("\nReport saved: %s" % report_out)


if __name__ == "__main__":
    main()
