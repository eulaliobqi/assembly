#!/usr/bin/env python3
"""
04_cross_validate_endosymbionts.py
Module 4, Layer 2 - cross-validate the DIAMOND/eggNOG-based endosymbiont
candidates (Layer 1, 01_taxonomic_summary.py) against Whokaryote+Tiara's
independent eukaryote/prokaryote classification of the assembled contigs
(structural, gene-content-based -- no sequence similarity to a reference
database, so it is not circular with the DIAMOND-based Layer 1 call).

Whokaryote only classifies contigs >=5000bp by default (most Trinity
transcripts, including single bacterial housekeeping genes, are shorter),
so most Layer 1 candidates are expected to be "not analyzed" rather than
confirmed or contradicted -- this coverage limit is reported explicitly,
not glossed over.

Usage:
  python 07_metagenomic_screen/04_cross_validate_endosymbionts.py
"""

import csv
import logging
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LAYER1_HITS = BASE / "results" / "endosymbiont_candidates" / "sulcia_sodalis_hits.tsv"
LAYER1_LOWPRIO = BASE / "results" / "endosymbiont_candidates" / "low_priority_pathogen_leads.tsv"
WHOKARYOTE_PRED = BASE / "results" / "whokaryote" / "whokaryote_predictions_T.tsv"
OUTDIR = BASE / "results" / "endosymbiont_candidates"

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def load_whokaryote():
    pred = {}
    with open(WHOKARYOTE_PRED, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            pred[row["contig"].strip()] = row["predicted"].strip()
    log.info("Whokaryote+Tiara: %d contigs classified (>=5000bp only)", len(pred))
    return pred


def cross_validate(hits_path, whokaryote_pred, expected_predicted="prokaryote"):
    rows = []
    with open(hits_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fieldnames = reader.fieldnames
        for row in reader:
            transcript_id = row.get("transcript_id", "").strip()
            wk_call = whokaryote_pred.get(transcript_id)
            if wk_call is None:
                status = "not_analyzed_below_5000bp"
            elif wk_call == expected_predicted:
                status = "concordant"
            else:
                status = f"discordant (whokaryote={wk_call})"
            rows.append({**row, "whokaryote_layer2": wk_call or "NA", "cross_validation_status": status})
    return rows, fieldnames


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    whokaryote_pred = load_whokaryote()

    symbiont_rows, symbiont_fields = cross_validate(LAYER1_HITS, whokaryote_pred, expected_predicted="prokaryote")
    lowprio_rows, lowprio_fields = cross_validate(LAYER1_LOWPRIO, whokaryote_pred, expected_predicted="prokaryote")

    out_fields = list(dict.fromkeys(
        symbiont_fields + lowprio_fields + ["whokaryote_layer2", "cross_validation_status"]
    ))
    out_path = OUTDIR / "endosymbionts_cross_validated.tsv"
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=out_fields, delimiter="\t")
        w.writeheader()
        w.writerows(symbiont_rows)
        w.writerows(lowprio_rows)

    n_total = len(symbiont_rows) + len(lowprio_rows)
    n_concordant = sum(1 for r in symbiont_rows + lowprio_rows if r["cross_validation_status"] == "concordant")
    n_discordant = sum(1 for r in symbiont_rows + lowprio_rows if r["cross_validation_status"].startswith("discordant"))
    n_not_analyzed = sum(1 for r in symbiont_rows + lowprio_rows if r["cross_validation_status"] == "not_analyzed_below_5000bp")

    report_path = OUTDIR / "cross_validation_report.txt"
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("ENDOSYMBIONT CROSS-VALIDATION REPORT (Layer 1 DIAMOND vs Layer 2 Whokaryote+Tiara)\n")
        fh.write("Mahanarva spectabilis - salivary gland transcriptome\n")
        fh.write("=" * 70 + "\n\n")
        fh.write(
            "Whokaryote's structural gene-content classifier only analyzes contigs\n"
            ">=5000bp; most Layer 1 candidates are single bacterial housekeeping\n"
            "genes on short Trinity transcripts, so most rows are expected to be\n"
            "'not_analyzed_below_5000bp' rather than confirmed/contradicted. This is\n"
            "a coverage limitation of Layer 2, not evidence against the Layer 1 call.\n\n"
        )
        fh.write(f"Total Layer 1 candidates: {n_total}\n")
        fh.write(f"  Concordant (Whokaryote = prokaryote): {n_concordant}\n")
        fh.write(f"  Discordant (Whokaryote = eukaryote):  {n_discordant}\n")
        fh.write(f"  Not analyzed (<5000bp):               {n_not_analyzed}\n")

    log.info("Cross-validated table: %s (%d rows)", out_path, n_total)
    log.info("Concordant: %d | Discordant: %d | Not analyzed (<5000bp): %d",
              n_concordant, n_discordant, n_not_analyzed)
    log.info("Report: %s", report_path)


if __name__ == "__main__":
    main()
