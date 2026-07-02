#!/usr/bin/env python3
"""
Fix merge bugs in results/annotation_complete.tsv without re-running the full
annotation pipeline.

Bugs fixed:
  1. go_terms / kegg_ko / eggnog_og / cog_category are empty for all rows
     because the eggNOG-mapper output was never correctly merged (protein_id
     mismatch / stale run). This script re-parses results/emapper.emapper.annotations
     using its real header line (never a hardcoded column index) and re-merges
     by protein_id.
  2. is_eukaryote / is_fungi are always 0 because the `lineage` column in
     annotation_complete.tsv holds the taxonkit *reformatted* lineage
     (k;p;c;o;f;g;s), which frequently omits the word "Fungi" for taxa with an
     empty kingdom rank. The full, unformatted lineage in column 2 of
     results/taxon_lineage.tsv always contains "Eukaryota"/"Fungi"/"Bacteria"/
     "Viruses" tokens and is used instead, keyed by diamond_taxids.
  3. CAZy annotations exist in the raw emapper output (column 19) but were
     never exposed in annotation_complete.tsv -- added as a new `cazy` column.

Usage:
  python 07_fix_annotation_merge.py
"""

import re
import shutil
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RESULTS = BASE / "results"

ANNOTATION_TSV = RESULTS / "annotation_complete.tsv"
EMAPPER_TSV = RESULTS / "emapper.emapper.annotations"
TAXON_LINEAGE_TSV = RESULTS / "taxon_lineage.tsv"
REPORT_TXT = RESULTS / "annotation_report.txt"

# reference values from a prior known-good run, hardcoded in
# 04_functional_analysis/plot_annotation.py -- used only as a sanity-check
# order-of-magnitude comparison, not an exact target.
REFERENCE = {
    "go_terms_nonempty": 9197,
    "kegg_ko_nonempty": 9197,
    "pfam_domains_nonempty": 7732,
    "eukaryote": 8455,
    "bacteria": 540,
    "fungi": 256,
    "virus": 30,
}


def parse_emapper(path):
    """Parse eggNOG-mapper TSV using its real '#query ...' header line."""
    header = None
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("##"):
                continue
            if line.startswith("#query"):
                header = line.lstrip("#").rstrip("\n").split("\t")
                continue
            if line.startswith("#") or not line.strip():
                continue
            rows.append(line.rstrip("\n").split("\t"))

    if header is None:
        raise RuntimeError("Could not find '#query' header line in " + str(path))

    df = pd.DataFrame(rows, columns=header)
    df = df.replace("-", "")

    keep = {
        "query": "protein_id",
        "eggNOG_OGs": "eggnog_og",
        "COG_category": "cog_category",
        "Description": "eggnog_desc",
        "GOs": "go_terms",
        "KEGG_ko": "kegg_ko",
        "KEGG_Pathway": "kegg_pathway",
        "CAZy": "cazy",
    }
    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise RuntimeError("emapper output missing expected columns: %s" % missing)

    return df[list(keep)].rename(columns=keep)


def parse_taxon_lineage(path):
    """taxid -> full (unformatted) lineage, e.g. 'cellular organisms;Eukaryota;...'."""
    lineage_by_taxid = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2 and parts[0].strip():
                lineage_by_taxid[parts[0].strip()] = parts[1].strip()
    return lineage_by_taxid


def classify_taxonomy(full_lineage):
    if not full_lineage:
        return 0, 0, 0, 0
    tokens = set(t.strip() for t in full_lineage.split(";"))
    is_euk = int("Eukaryota" in tokens)
    is_bac = int("Bacteria" in tokens)
    is_fun = int("Fungi" in tokens)
    is_vir = int(
        "Viruses" in tokens or any(re.search(r"viridae$", t, re.I) for t in tokens)
    )
    return is_euk, is_bac, is_fun, is_vir


def main():
    print("Reading %s ..." % ANNOTATION_TSV)
    annot = pd.read_csv(ANNOTATION_TSV, sep="\t", dtype=str, keep_default_na=False)

    taxid_col = "diamond_taxids" if "diamond_taxids" in annot.columns else "diamond_taxid"
    if taxid_col not in annot.columns:
        raise RuntimeError(
            "Could not find a diamond taxid column in annotation_complete.tsv "
            "(looked for 'diamond_taxids' and 'diamond_taxid')"
        )

    print("Backing up original to %s.bak" % ANNOTATION_TSV.name)
    shutil.copy2(ANNOTATION_TSV, ANNOTATION_TSV.with_suffix(".tsv.bak"))

    print("Re-parsing %s ..." % EMAPPER_TSV)
    em = parse_emapper(EMAPPER_TSV)
    em = em.drop_duplicates(subset="protein_id", keep="first")

    # drop the old (broken) eggNOG-derived columns before merging in fresh ones
    old_eggnog_cols = ["go_terms", "kegg_ko", "kegg_pathway", "eggnog_og", "cog_category", "eggnog_desc"]
    annot = annot.drop(columns=[c for c in old_eggnog_cols if c in annot.columns])

    annot = annot.merge(em, on="protein_id", how="left")
    for c in ["eggnog_og", "cog_category", "eggnog_desc", "go_terms", "kegg_ko", "kegg_pathway", "cazy"]:
        annot[c] = annot[c].fillna("")

    print("Re-parsing %s ..." % TAXON_LINEAGE_TSV)
    lineage_by_taxid = parse_taxon_lineage(TAXON_LINEAGE_TSV)

    flags = annot[taxid_col].map(lambda t: classify_taxonomy(lineage_by_taxid.get(str(t).strip(), "")))
    annot["is_eukaryote"] = [f[0] for f in flags]
    annot["is_bacteria"] = [f[1] for f in flags]
    annot["is_fungi"] = [f[2] for f in flags]
    annot["is_virus"] = [f[3] for f in flags]

    # restore a sensible column order: keep everything, move cazy next to the
    # other eggNOG-derived columns and diamond_title last (unchanged position)
    cols = list(annot.columns)
    cols.remove("cazy")
    cols.remove("diamond_title")
    insert_at = cols.index("eggnog_desc") + 1
    cols = cols[:insert_at] + ["cazy"] + cols[insert_at:] + ["diamond_title"]
    annot = annot[cols]

    print("Writing corrected %s ..." % ANNOTATION_TSV)
    annot.to_csv(ANNOTATION_TSV, sep="\t", index=False)

    # --- sanity-check summary ---------------------------------------------
    total = len(annot)
    go_nonempty = (annot["go_terms"] != "").sum()
    kegg_nonempty = (annot["kegg_ko"] != "").sum()
    pfam_nonempty = (annot["pfam_domains"] != "").sum() if "pfam_domains" in annot.columns else 0
    cazy_nonempty = (annot["cazy"] != "").sum()
    tax = {
        "eukaryote": int(annot["is_eukaryote"].astype(int).sum()),
        "bacteria": int(annot["is_bacteria"].astype(int).sum()),
        "fungi": int(annot["is_fungi"].astype(int).sum()),
        "virus": int(annot["is_virus"].astype(int).sum()),
    }
    tax["unclassified"] = total - sum(
        1 for _, r in annot.iterrows()
        if int(r["is_eukaryote"]) or int(r["is_bacteria"]) or int(r["is_fungi"]) or int(r["is_virus"])
    )

    lines = [
        "=" * 60,
        "  AutoAnnotate merge fix - Summary Report (corrected)",
        "=" * 60,
        "  Input proteins        : %d" % total,
        "  With GO terms         : %d (%.1f%%)  [ref: %d]" % (
            go_nonempty, 100.0 * go_nonempty / total, REFERENCE["go_terms_nonempty"]),
        "  With KEGG KO          : %d (%.1f%%)  [ref: %d]" % (
            kegg_nonempty, 100.0 * kegg_nonempty / total, REFERENCE["kegg_ko_nonempty"]),
        "  With Pfam domain      : %d (%.1f%%)  [ref: %d]" % (
            pfam_nonempty, 100.0 * pfam_nonempty / total, REFERENCE["pfam_domains_nonempty"]),
        "  With CAZy annotation  : %d (%.1f%%)  [new column]" % (
            cazy_nonempty, 100.0 * cazy_nonempty / total),
        "",
        "  Taxonomic classification of best hits (recomputed from full lineage):",
        "    Eukaryota           : %d  [ref: %d]" % (tax["eukaryote"], REFERENCE["eukaryote"]),
        "    Bacteria            : %d  [ref: %d]" % (tax["bacteria"], REFERENCE["bacteria"]),
        "    Fungi               : %d  [ref: %d]" % (tax["fungi"], REFERENCE["fungi"]),
        "    Viruses             : %d  [ref: %d]" % (tax["virus"], REFERENCE["virus"]),
        "    Unclassified        : %d" % tax["unclassified"],
        "=" * 60,
    ]
    report = "\n".join(lines)
    print(report)
    REPORT_TXT.write_text(report + "\n", encoding="utf-8")
    print("Report saved: %s" % REPORT_TXT)


if __name__ == "__main__":
    main()
