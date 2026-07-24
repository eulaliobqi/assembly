#!/usr/bin/env python3
"""
effector_candidates.py
Module 3: candidate salivary effector/toxin prioritization for the
amarelao phytotoxemia hypothesis.

Joins:
  - results/annotation_complete.tsv (DIAMOND/eggNOG/Pfam + cazy column,
    the latter updated by 03_annotation/08_cazy_annotation.sh)
  - results/secretome/secretome_all.tsv (TMbed classical secretome call,
    see 05_secretome/secretome_predict.py)
  - expression/salmon-quant.sf (TPM, matched by stripping the TransDecoder
    ".pN" suffix from protein_id -> transcript_id, same convention as
    07_metagenomic_screen/01_taxonomic_summary.py)

Filter (as scoped/approved for this project): classical secretome AND at
least one curated toxin/effector term or domain match (see CURATED_TERMS
below -- venom-like proteases, salivary secreted peptides, laccase,
mucins, phospholipases, EF-hand/Ca-binding, GH28/GH5 cell-wall-degrading
CAZymes). No proteins outside these two independently-verified sources
are reported as candidates -- ranking is additive (secreted + curated
match count + TPM), not ML/inferred.

Usage:
  python 06_effector_prioritization/effector_candidates.py
"""

import csv
import logging
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ANNOTATION = BASE / "results" / "annotation_complete.tsv"
SECRETOME = BASE / "results" / "secretome" / "secretome_all.tsv"
SALMON_SF = BASE / "expression" / "salmon-quant.sf"
OUTDIR = BASE / "results" / "effector_candidates"

TRANSCRIPT_SUFFIX_RE = re.compile(r"\.p\d+$")

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

# Curated toxin/effector terms and domains, drawn from the annotation
# already surfaced in the project diagnosis (README Biological
# Motivation / Key Results) -- not invented for this script.
CURATED_TERMS = {
    "venom_protease":      re.compile(r"venom.*protease", re.I),
    "dpp4":                re.compile(r"dipeptidyl peptidase|DPP.?4", re.I),
    "venom_carboxypeptidase": re.compile(r"venom.*carboxypeptidase|carboxypeptidase.*venom", re.I),
    "salivary_secreted":   re.compile(r"salivary secreted (peptide|protein)", re.I),
    "nos_salivary":        re.compile(r"nitric oxide synthase", re.I),
    "laccase":             re.compile(r"laccase", re.I),
    "mucin":               re.compile(r"mucin", re.I),
    "phospholipase":       re.compile(r"phospholipase\s*[AB]2?", re.I),
    "ef_hand_ca_binding":  re.compile(r"EF.?hand|calcium.binding|Ca2\+.binding", re.I),
    "gh28_gh5_cazy":       re.compile(r"\bGH28\b|\bGH5\b|cellulase|pectinase", re.I),
}

TEXT_FIELDS = [
    "diamond_subject", "diamond_sciname", "diamond_title",
    "pfam_domains", "eggnog_desc", "cazy",
]


def load_annotation():
    rows = {}
    with open(ANNOTATION, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            pid = row.get("protein_id", "").strip()
            if pid:
                rows[pid] = row
    log.info("Loaded annotation for %d proteins", len(rows))
    return rows


def load_secretome():
    rows = {}
    with open(SECRETOME, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            pid = row.get("protein_id", "").strip()
            if pid:
                rows[pid] = row
    log.info("Loaded secretome predictions for %d proteins", len(rows))
    return rows


def load_tpm():
    tpm = {}
    with open(SALMON_SF, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            name = row.get("Name", "").strip()
            try:
                tpm[name] = float(row.get("TPM", 0.0))
            except ValueError:
                tpm[name] = 0.0
    log.info("Loaded TPM for %d transcripts", len(tpm))
    return tpm


def protein_to_transcript(protein_id):
    return TRANSCRIPT_SUFFIX_RE.sub("", protein_id)


def match_curated_terms(annot_row):
    text = " ".join(annot_row.get(f, "") or "" for f in TEXT_FIELDS)
    return [name for name, pat in CURATED_TERMS.items() if pat.search(text)]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    annot = load_annotation()
    secretome = load_secretome()
    tpm = load_tpm()

    candidates = []
    for pid, sec in secretome.items():
        if sec.get("is_secreted", "").strip() not in ("True", "1", "true"):
            continue
        a = annot.get(pid, {})
        matches = match_curated_terms(a)
        if not matches:
            continue

        transcript_id = protein_to_transcript(pid)
        protein_tpm = tpm.get(transcript_id, 0.0)

        candidates.append({
            "protein_id": pid,
            "transcript_id": transcript_id,
            "tpm": round(protein_tpm, 4),
            "n_curated_matches": len(matches),
            "curated_terms": ";".join(matches),
            "sp_prob": sec.get("sp_prob", ""),
            "tm_count": sec.get("tm_count", ""),
            "gene_name": a.get("gene_name", ""),
            "diamond_subject": a.get("diamond_subject", ""),
            "diamond_sciname": a.get("diamond_sciname", ""),
            "diamond_pident": a.get("diamond_pident", ""),
            "pfam_domains": a.get("pfam_domains", ""),
            "eggnog_desc": a.get("eggnog_desc", ""),
            "cazy": a.get("cazy", ""),
            "go_terms": a.get("go_terms", ""),
        })

    # Simple additive rank: curated-term breadth first, then expression.
    candidates.sort(key=lambda r: (r["n_curated_matches"], r["tpm"]), reverse=True)

    fields = [
        "protein_id", "transcript_id", "tpm", "n_curated_matches", "curated_terms",
        "sp_prob", "tm_count", "gene_name", "diamond_subject", "diamond_sciname",
        "diamond_pident", "pfam_domains", "eggnog_desc", "cazy", "go_terms",
    ]
    out_path = OUTDIR / "effector_candidates_ranked.tsv"
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        w.writeheader()
        w.writerows(candidates)

    log.info("Classical secretome: %d proteins", sum(1 for s in secretome.values() if s.get("is_secreted", "").strip() in ("True", "1", "true")))
    log.info("Candidates (secreted AND curated-term match): %d -> %s", len(candidates), out_path)

    per_term = {}
    for c in candidates:
        for t in c["curated_terms"].split(";"):
            per_term[t] = per_term.get(t, 0) + 1
    report_path = OUTDIR / "effector_candidates_report.txt"
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("EFFECTOR/TOXIN CANDIDATE PRIORITIZATION REPORT\n")
        fh.write("Mahanarva spectabilis - salivary gland proteins\n")
        fh.write("=" * 62 + "\n\n")
        fh.write("Criteria: classical secretome (TMbed) AND >=1 curated toxin/effector term\n\n")
        fh.write(f"Total candidates: {len(candidates)}\n\n")
        fh.write("Candidates per curated term:\n")
        for t, n in sorted(per_term.items(), key=lambda kv: kv[1], reverse=True):
            fh.write(f"  {t:<25} {n:>5}\n")
    log.info("Report: %s", report_path)


if __name__ == "__main__":
    main()
