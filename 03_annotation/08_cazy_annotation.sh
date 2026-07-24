#!/usr/bin/env bash
# =============================================================================
# Step 8 (dedicated) — dbCAN CAZyme annotation
#
# The eggNOG-mapper-derived `cazy` column in annotation_complete.tsv only
# covers 1.4% of proteins (175/12,445) and found zero GH28/GH5 hits
# (cellulase/pectinase, classically associated with cell-wall-degrading
# phytotoxic effectors) -- known low sensitivity, motivating this
# dedicated run against the real dbCAN database (DIAMOND + dbCAN-HMM +
# dbCAN-sub, run_dbcan CLI, bioconda `dbcan` package).
#
# Usage:
#   bash 03_annotation/08_cazy_annotation.sh /path/to/dbcan_db_dir
# =============================================================================
set -euo pipefail

DB_DIR="${1:?Usage: 08_cazy_annotation.sh /path/to/dbcan_db_dir}"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT_PEP="${BASE_DIR}/data/transdecoder/trinity_nr95.fasta.transdecoder.pep"
OUT_DIR="${BASE_DIR}/results/cazy"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate cazy

# One-time database download (skips files already present).
run_dbcan database --no-cgc --db_dir "${DB_DIR}"

run_dbcan CAZyme_annotation \
    --mode protein \
    --output_dir "${OUT_DIR}" \
    --input_raw_data "${INPUT_PEP}" \
    --db_dir "${DB_DIR}" \
    --threads 16

python "${BASE_DIR}/03_annotation/09_merge_cazy.py"
