#!/usr/bin/env python3
"""
09_merge_cazy.py
Merge the dedicated dbCAN CAZyme_annotation result (results/cazy/overview.tsv)
into results/annotation_complete.tsv, replacing the sparse/low-sensitivity
eggNOG-derived `cazy` column (see README Known Issues -- 1.4% coverage,
0 GH28/GH5 hits).

overview.tsv columns: Gene ID, EC#, dbCAN_hmm, dbCAN_sub, DIAMOND,
#ofTools, Recommend Results, Substrate. A protein's new cazy value is the
';'-joined, de-duplicated set of non-'-' family calls across the three
methods (dbCAN_hmm, dbCAN_sub, DIAMOND).

Usage:
  python 03_annotation/09_merge_cazy.py
"""

import csv
import logging
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ANNOTATION = BASE / "results" / "annotation_complete.tsv"
OVERVIEW = BASE / "results" / "cazy" / "overview.tsv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

METHOD_COLS = ["dbCAN_hmm", "dbCAN_sub", "DIAMOND"]


def load_cazy_calls():
    calls = {}
    with open(OVERVIEW, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            pid = row["Gene ID"].strip()
            families = []
            for col in METHOD_COLS:
                val = row.get(col, "-").strip()
                if val and val != "-":
                    families.extend(f.strip() for f in val.split("+") if f.strip())
            if families:
                calls[pid] = ";".join(dict.fromkeys(families))
    log.info("Dedicated dbCAN calls: %d proteins with >=1 CAZy family", len(calls))
    return calls


def main():
    calls = load_cazy_calls()

    backup = ANNOTATION.with_suffix(".tsv.bak_precazy")
    if not backup.exists():
        shutil.copy(ANNOTATION, backup)
        log.info("Backup saved: %s", backup)

    with open(ANNOTATION, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fieldnames = reader.fieldnames
        rows = list(reader)

    n_updated = 0
    for row in rows:
        pid = row["protein_id"].strip()
        row["cazy"] = calls.get(pid, "")
        if pid in calls:
            n_updated += 1

    with open(ANNOTATION, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    n_gh28_gh5 = sum(
        1 for r in rows
        if any(f.split("_")[0] in ("GH28", "GH5") for f in r["cazy"].split(";") if f)
    )
    log.info("annotation_complete.tsv updated: %d/%d proteins now have a dbCAN cazy call", n_updated, len(rows))
    log.info("Proteins with a GH28 or GH5* family call: %d", n_gh28_gh5)

    update_cazy_line_in_report(len(calls), len(rows))


def update_cazy_line_in_report(n_cazy, total):
    """Refresh the 'With CAZy annotation' line in the existing annotation_report.txt
    (all other lines there are unaffected by this script -- GO/KEGG/Pfam/taxonomy)."""
    report_path = BASE / "results" / "annotation_report.txt"
    if not report_path.exists():
        log.warning("%s not found, skipping report refresh", report_path)
        return
    text = report_path.read_text(encoding="utf-8")
    new_line = "  With CAZy annotation  : %d (%.1f%%)  [dbCAN3, dedicated run]" % (
        n_cazy, 100.0 * n_cazy / total)
    lines = [new_line if line.strip().startswith("With CAZy annotation") else line
             for line in text.splitlines()]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("Refreshed CAZy line in %s", report_path)


if __name__ == "__main__":
    main()
