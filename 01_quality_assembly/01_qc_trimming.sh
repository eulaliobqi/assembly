#!/usr/bin/env bash
# =============================================================================
# Script: 01_qc_trimming.sh
# Project: Mahanarva spectabilis Salivary Gland Transcriptome
# Purpose: Quality control and adapter trimming of raw RNA-seq reads
#
# Tools required (conda env: assembly):
#   - FastQC >= 0.12.1
#   - MultiQC >= 1.21
#   - fastp >= 0.23.4
#
# Pipeline overview:
#   1. FastQC on raw reads
#   2. MultiQC aggregation of raw QC reports
#   3. fastp trimming (quality filter + adapter removal)
#   4. FastQC on trimmed reads
#   5. MultiQC aggregation of trimmed QC reports
#
# Quality checkpoints (evaluate MultiQC reports before proceeding):
#   - Mean Phred quality score >= Q28 across all positions
#   - Fraction of N bases < 5% per read
#   - Read retention after trimming >= 80% of raw input
#   - GC content consistent with expected transcriptomic distribution
#
# Usage:
#   bash 01_quality_assembly/01_qc_trimming.sh
# =============================================================================

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

# =============================================================================
# CONFIGURATION - Edit these paths before running
# =============================================================================

# Input raw reads (paired-end FASTQ; .gz compressed expected)
R1="data/raw/sample_R1.fastq.gz"
R2="data/raw/sample_R2.fastq.gz"

# Sample name (used for output file naming)
SAMPLE="mahanarva_salivary_gland"

# Output directories
DIR_RAW_QC="results/qc/raw"
DIR_TRIMMED="data/trimmed"
DIR_TRIMMED_QC="results/qc/trimmed"

# Number of threads for parallel processing
THREADS=8

# fastp trimming parameters
QUALITY_PHRED=20         # Minimum base quality score (Phred scale)
MIN_LENGTH=50            # Minimum read length after trimming
MIN_COMPLEXITY=30        # Minimum per-read complexity (%) to filter dust/low-complexity

# =============================================================================
# SETUP - Create output directories
# =============================================================================

echo "======================================================"
echo " Step 1/5: Setting up output directories"
echo "======================================================"

mkdir -p "${DIR_RAW_QC}"
mkdir -p "${DIR_TRIMMED}"
mkdir -p "${DIR_TRIMMED_QC}"

echo "Output directories created."

# =============================================================================
# STEP 1: FastQC on raw reads
# =============================================================================

echo ""
echo "======================================================"
echo " Step 2/5: FastQC - Raw reads"
echo "======================================================"
echo "Input R1: ${R1}"
echo "Input R2: ${R2}"

fastqc \
    --outdir "${DIR_RAW_QC}" \
    --threads "${THREADS}" \
    --extract \
    "${R1}" \
    "${R2}"

echo "FastQC (raw) complete. Reports saved to: ${DIR_RAW_QC}"

# =============================================================================
# STEP 2: MultiQC on raw FastQC reports
# =============================================================================

echo ""
echo "======================================================"
echo " Step 3/5: MultiQC - Aggregating raw QC reports"
echo "======================================================"

multiqc \
    "${DIR_RAW_QC}" \
    --outdir "${DIR_RAW_QC}" \
    --filename "multiqc_raw_report" \
    --title "Raw Reads QC - Mahanarva spectabilis Salivary Gland" \
    --force

echo "MultiQC (raw) report saved to: ${DIR_RAW_QC}/multiqc_raw_report.html"
echo ""
echo ">>> CHECKPOINT: Review ${DIR_RAW_QC}/multiqc_raw_report.html before proceeding."
echo "    Expected: Phred >= Q28 at most positions, GC ~40-60%, no adapter contamination."

# =============================================================================
# STEP 3: fastp trimming
#
# Parameter rationale for Hemiptera transcriptomics:
#   --qualified_quality_phred 20   : Minimum Phred Q20 per base (standard for RNA-seq)
#   --unqualified_percent_limit 40 : Allow up to 40% of bases below Q20 before discarding
#   --n_base_limit 5               : Discard reads with >5 N bases
#   --length_required 50           : Discard reads shorter than 50 bp after trimming
#   --detect_adapter_for_pe        : Auto-detect adapter sequences (robust for unknown library preps)
#   --low_complexity_filter        : Remove reads with low sequence complexity (e.g., poly-A)
#   --complexity_threshold 30      : Minimum complexity threshold (30%)
#   --correction                   : Enable overlap-based error correction for PE reads
#   --thread                       : Parallel threads
# =============================================================================

echo ""
echo "======================================================"
echo " Step 4/5: fastp - Adapter trimming and quality filtering"
echo "======================================================"

TRIMMED_R1="${DIR_TRIMMED}/${SAMPLE}_R1_trimmed.fastq.gz"
TRIMMED_R2="${DIR_TRIMMED}/${SAMPLE}_R2_trimmed.fastq.gz"
FASTP_JSON="${DIR_TRIMMED}/${SAMPLE}_fastp.json"
FASTP_HTML="${DIR_TRIMMED}/${SAMPLE}_fastp.html"
UNPAIRED_R1="${DIR_TRIMMED}/${SAMPLE}_R1_unpaired.fastq.gz"
UNPAIRED_R2="${DIR_TRIMMED}/${SAMPLE}_R2_unpaired.fastq.gz"

fastp \
    --in1 "${R1}" \
    --in2 "${R2}" \
    --out1 "${TRIMMED_R1}" \
    --out2 "${TRIMMED_R2}" \
    --unpaired1 "${UNPAIRED_R1}" \
    --unpaired2 "${UNPAIRED_R2}" \
    --qualified_quality_phred "${QUALITY_PHRED}" \
    --unqualified_percent_limit 40 \
    --n_base_limit 5 \
    --length_required "${MIN_LENGTH}" \
    --detect_adapter_for_pe \
    --low_complexity_filter \
    --complexity_threshold "${MIN_COMPLEXITY}" \
    --correction \
    --thread "${THREADS}" \
    --json "${FASTP_JSON}" \
    --html "${FASTP_HTML}" \
    --report_title "fastp QC Report - ${SAMPLE}"

echo "fastp trimming complete."
echo "Trimmed R1: ${TRIMMED_R1}"
echo "Trimmed R2: ${TRIMMED_R2}"
echo "QC Report:  ${FASTP_HTML}"

# =============================================================================
# Post-trimming quality checkpoint
# Parse fastp JSON to check read retention
# =============================================================================

echo ""
echo ">>> CHECKPOINT: Verifying read retention >= 80%..."

RETENTION=$(python3 -c "
import json, sys
with open('${FASTP_JSON}') as f:
    data = json.load(f)
total_in = data['summary']['before_filtering']['total_reads']
total_out = data['summary']['after_filtering']['total_reads']
pct = (total_out / total_in) * 100
print(f'  Total reads input:    {total_in:,}')
print(f'  Total reads output:   {total_out:,}')
print(f'  Retention rate:       {pct:.1f}%')
if pct < 80:
    print('  WARNING: Retention < 80%. Check fastp parameters.')
    sys.exit(1)
else:
    print('  PASS: Retention >= 80%.')
")
echo "${RETENTION}"

# =============================================================================
# STEP 4: FastQC on trimmed reads
# =============================================================================

echo ""
echo "======================================================"
echo " Step 5a/5: FastQC - Trimmed reads"
echo "======================================================"

fastqc \
    --outdir "${DIR_TRIMMED_QC}" \
    --threads "${THREADS}" \
    --extract \
    "${TRIMMED_R1}" \
    "${TRIMMED_R2}"

echo "FastQC (trimmed) complete. Reports saved to: ${DIR_TRIMMED_QC}"

# =============================================================================
# STEP 5: MultiQC on trimmed FastQC reports
# =============================================================================

echo ""
echo "======================================================"
echo " Step 5b/5: MultiQC - Aggregating trimmed QC reports"
echo "======================================================"

multiqc \
    "${DIR_TRIMMED_QC}" \
    "${FASTP_JSON}" \
    --outdir "${DIR_TRIMMED_QC}" \
    --filename "multiqc_trimmed_report" \
    --title "Trimmed Reads QC - Mahanarva spectabilis Salivary Gland" \
    --force

echo "MultiQC (trimmed) report saved to: ${DIR_TRIMMED_QC}/multiqc_trimmed_report.html"

# =============================================================================
# FINAL SUMMARY
# =============================================================================

echo ""
echo "======================================================"
echo " QC and Trimming Complete"
echo "======================================================"
echo ""
echo "Output files:"
echo "  Trimmed R1:         ${TRIMMED_R1}"
echo "  Trimmed R2:         ${TRIMMED_R2}"
echo "  fastp HTML report:  ${FASTP_HTML}"
echo "  Raw MultiQC:        ${DIR_RAW_QC}/multiqc_raw_report.html"
echo "  Trimmed MultiQC:    ${DIR_TRIMMED_QC}/multiqc_trimmed_report.html"
echo ""
echo "Quality checkpoints to verify before assembly:"
echo "  [1] Mean Phred quality >= Q28 at all positions"
echo "  [2] Fraction N bases < 5%"
echo "  [3] Read retention >= 80%"
echo "  [4] No remaining adapter sequences"
echo ""
echo "Next step: bash 01_quality_assembly/02_trinity_assembly.sh"
