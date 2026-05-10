#!/usr/bin/env bash
# =============================================================================
# Script: 03_stats_busco.sh
# Project: Mahanarva spectabilis Salivary Gland Transcriptome
# Purpose: Assembly quality evaluation using TrinityStats, seqkit, and BUSCO
#
# Tools required (conda env: assembly):
#   - Trinity (for TrinityStats.pl utility)
#   - seqkit >= 2.8.0
#   - BUSCO >= 5.7.0
#
# Quality thresholds for acceptance:
#   - N50 > 1000 bp (median transcript reconstructed well)
#   - Total genes/loci: 15,000 - 60,000 (reasonable range for insect transcriptome)
#   - BUSCO complete (C): > 70%
#   - BUSCO fragmented (F): < 15%
#   - BUSCO missing (M): < 30%
#
# IMPORTANT NOTE on BUSCO completeness for salivary gland transcriptomics:
#   Complete BUSCO scores are expected to be LOWER than for whole-body or
#   mixed-tissue transcriptomes because the salivary gland represents a single,
#   specialized tissue. Many housekeeping and developmental genes are not
#   expressed in this tissue at detectable levels, and thus will not be
#   assembled. A score of 60-75% complete for a tissue-specific transcriptome
#   can reflect genuine biology rather than assembly failure.
#   Compare against other Hemiptera salivary gland studies for context.
#
# Usage:
#   bash 02_assembly_evaluation/03_stats_busco.sh
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

SAMPLE="mahanarva_salivary_gland"

# Input assemblies (output of 02_trinity_assembly.sh)
TRINITY_FASTA="results/trinity_out/Trinity.fasta"
CDHIT_FASTA="results/assembly/${SAMPLE}_cdhit95.fasta"

# Minimum contig length for filtered statistics
MIN_LEN=300

# BUSCO configuration
BUSCO_LINEAGE="insecta_odb10"   # Use insecta_odb10 for Hemiptera (order within Insecta)
                                 # Alternative: hemiptera_odb10 if available in your BUSCO version
BUSCO_MODE="transcriptome"       # Evaluate transcript (nucleotide) sequences, not proteins
BUSCO_DOWNLOADS="./busco_downloads"  # Where BUSCO will cache lineage datasets

# Threads
THREADS=16

# Output directory
EVAL_OUT="results/evaluation"

# =============================================================================
# SETUP
# =============================================================================

echo "======================================================"
echo " Setup: Assembly Evaluation"
echo "======================================================"

mkdir -p "${EVAL_OUT}"
mkdir -p "${EVAL_OUT}/busco_trinity"
mkdir -p "${EVAL_OUT}/busco_cdhit"

echo "Evaluating assemblies:"
echo "  Raw Trinity:  ${TRINITY_FASTA}"
echo "  CD-HIT-EST:   ${CDHIT_FASTA}"

# =============================================================================
# STEP 1: TrinityStats.pl - Basic assembly statistics
#
# TrinityStats.pl reports:
#   - Total assembled bases
#   - Total number of transcripts
#   - Number of genes (components)
#   - Contig N10, N20, ... N90, N50
#   - Median and mean contig lengths
#   - GC content
#
# Quality thresholds (as comments):
#   - N50 > 1000 bp: Indicates that at least half the assembly is in transcripts
#                    longer than 1 kb, suggesting good reconstruction quality.
#   - Total genes 15,000-60,000: Expected range for insect transcriptomes.
#                    Salivary gland may trend toward the lower end (tissue-specific).
#   - Mean contig length > 800 bp: Suggests adequate read depth and k-mer coverage.
# =============================================================================

echo ""
echo "======================================================"
echo " Step 1/3: TrinityStats.pl - Assembly statistics"
echo "======================================================"

TRINITY_STATS_OUT="${EVAL_OUT}/trinity_stats.txt"

echo "--- Raw Trinity assembly statistics ---"
TrinityStats.pl "${TRINITY_FASTA}" 2>&1 | tee "${TRINITY_STATS_OUT}"

echo ""
echo "TrinityStats report saved to: ${TRINITY_STATS_OUT}"

# TrinityStats on CD-HIT clustered assembly
CDHIT_STATS_OUT="${EVAL_OUT}/cdhit_stats.txt"
echo ""
echo "--- CD-HIT-EST clustered assembly statistics ---"
TrinityStats.pl "${CDHIT_FASTA}" 2>&1 | tee "${CDHIT_STATS_OUT}"

echo ""
echo "CD-HIT stats report saved to: ${CDHIT_STATS_OUT}"

# =============================================================================
# STEP 2: seqkit stats - Detailed statistics with length filtering
#
# seqkit provides additional metrics including:
#   - Number of sequences
#   - Sum of lengths
#   - Min, max, mean, and median length
#   - N50 and Q20/Q30 (when used with quality-enabled inputs)
#
# We filter to >= MIN_LEN bp to match downstream annotation criteria.
# =============================================================================

echo ""
echo "======================================================"
echo " Step 2/3: seqkit stats - Contig length distribution"
echo "======================================================"

SEQKIT_STATS_OUT="${EVAL_OUT}/seqkit_stats.tsv"

echo "All transcripts (no length filter):"
seqkit stats \
    --all \
    --tabular \
    "${CDHIT_FASTA}" | tee "${SEQKIT_STATS_OUT}"

echo ""
echo "Transcripts >= ${MIN_LEN} bp:"
seqkit seq \
    --min-len "${MIN_LEN}" \
    "${CDHIT_FASTA}" | \
    seqkit stats \
        --all \
        --tabular | \
    tee -a "${SEQKIT_STATS_OUT}"

echo ""
echo "seqkit statistics saved to: ${SEQKIT_STATS_OUT}"

# Length distribution histogram (counts per 500 bp bin)
echo ""
echo "Contig length distribution (500 bp bins, transcripts >= ${MIN_LEN} bp):"
seqkit seq --min-len "${MIN_LEN}" "${CDHIT_FASTA}" | \
    seqkit fx2tab --length --name --header-line | \
    awk 'NR>1 {bin=int($2/500)*500; counts[bin]++}
         END {for (b in counts) printf "%d\t%d\n", b, counts[b]}' | \
    sort -k1,1n | \
    awk '{printf "  %7d bp: %s\n", $1, substr("##################################################", 1, int($2/5))}'

# =============================================================================
# STEP 3: BUSCO - Benchmarking Universal Single-Copy Orthologs
#
# BUSCO measures assembly completeness by searching for conserved single-copy
# orthologs expected to be present in nearly all members of a given lineage.
#
# Database: insecta_odb10
#   Contains 1,367 universal single-copy orthologs from Insecta.
#   Used here because Mahanarva spectabilis is Hemiptera (within Insecta).
#   If insecta_odb10 is unavailable, hemiptera_odb10 or arthropoda_odb10 can be used.
#
# Mode: transcriptome
#   Evaluates the transcript-level assembly (nucleotide FASTA).
#   Alternative mode 'proteins' would use the TransDecoder .pep file.
#
# BUSCO result categories:
#   C = Complete (found as single copy)
#   D = Duplicated (found as multiple copies; isoforms may inflate this)
#   F = Fragmented (found but incomplete)
#   M = Missing (not found)
#
# Interpretation for tissue-specific transcriptomes:
#   A salivary gland transcriptome is expected to show lower completeness than
#   a whole-body transcriptome because tissue-specific genes not expressed in
#   the salivary gland will be classified as Missing. This is EXPECTED and does
#   NOT indicate a low-quality assembly. Context: published Hemiptera salivary
#   gland transcriptomes typically report 55-80% complete BUSCOs.
#
# Thresholds (for a tissue-specific insect transcriptome):
#   C > 70%  : Good completeness for salivary gland tissue
#   F < 15%  : Low fragmentation expected with good Trinity assembly
#   M < 30%  : Some missing expected due to tissue specificity
# =============================================================================

echo ""
echo "======================================================"
echo " Step 3/3: BUSCO - Completeness assessment"
echo "======================================================"
echo "Lineage database: ${BUSCO_LINEAGE}"
echo "Mode: ${BUSCO_MODE}"
echo ""
echo "NOTE: Salivary gland is a specialized tissue. Missing BUSCOs may reflect"
echo "      tissue-specific gene expression rather than assembly quality issues."
echo ""

# --- BUSCO on CD-HIT clustered assembly ---
echo "Running BUSCO on CD-HIT-EST clustered assembly..."

BUSCO_CDHIT_OUT="${EVAL_OUT}/busco_cdhit"

busco \
    --input "${CDHIT_FASTA}" \
    --out "busco_${SAMPLE}_cdhit" \
    --out_path "${BUSCO_CDHIT_OUT}" \
    --lineage_dataset "${BUSCO_LINEAGE}" \
    --mode "${BUSCO_MODE}" \
    --cpu "${THREADS}" \
    --download_path "${BUSCO_DOWNLOADS}" \
    --force

echo ""
echo "BUSCO (CD-HIT assembly) complete."
echo "Results in: ${BUSCO_CDHIT_OUT}/busco_${SAMPLE}_cdhit/"

# --- BUSCO on raw Trinity assembly (for comparison) ---
echo ""
echo "Running BUSCO on raw Trinity assembly (for comparison)..."

BUSCO_TRINITY_OUT="${EVAL_OUT}/busco_trinity"

busco \
    --input "${TRINITY_FASTA}" \
    --out "busco_${SAMPLE}_trinity" \
    --out_path "${BUSCO_TRINITY_OUT}" \
    --lineage_dataset "${BUSCO_LINEAGE}" \
    --mode "${BUSCO_MODE}" \
    --cpu "${THREADS}" \
    --download_path "${BUSCO_DOWNLOADS}" \
    --force

echo ""
echo "BUSCO (raw Trinity assembly) complete."
echo "Results in: ${BUSCO_TRINITY_OUT}/busco_${SAMPLE}_trinity/"

# =============================================================================
# BUSCO SUMMARY COMPARISON
# =============================================================================

echo ""
echo "======================================================"
echo " BUSCO Summary Comparison"
echo "======================================================"

# Print short summary from both runs
SUMMARY_CDHIT="${BUSCO_CDHIT_OUT}/busco_${SAMPLE}_cdhit/short_summary.specific.${BUSCO_LINEAGE}.busco_${SAMPLE}_cdhit.txt"
SUMMARY_TRINITY="${BUSCO_TRINITY_OUT}/busco_${SAMPLE}_trinity/short_summary.specific.${BUSCO_LINEAGE}.busco_${SAMPLE}_trinity.txt"

if [ -f "${SUMMARY_CDHIT}" ]; then
    echo "--- BUSCO: CD-HIT-EST clustered assembly ---"
    cat "${SUMMARY_CDHIT}"
fi

if [ -f "${SUMMARY_TRINITY}" ]; then
    echo ""
    echo "--- BUSCO: Raw Trinity assembly ---"
    cat "${SUMMARY_TRINITY}"
fi

# =============================================================================
# GENERATE MultiQC-compatible BUSCO summary (optional)
# =============================================================================

echo ""
echo "Generating combined evaluation report..."

REPORT="${EVAL_OUT}/assembly_evaluation_report.txt"

{
    echo "============================================================"
    echo "Assembly Evaluation Report - ${SAMPLE}"
    echo "Date: $(date)"
    echo "============================================================"
    echo ""
    echo "=== TrinityStats: CD-HIT-EST Assembly ==="
    cat "${CDHIT_STATS_OUT}"
    echo ""
    echo "=== seqkit stats ==="
    cat "${SEQKIT_STATS_OUT}"
    echo ""
    if [ -f "${SUMMARY_CDHIT}" ]; then
        echo "=== BUSCO: CD-HIT-EST assembly ==="
        cat "${SUMMARY_CDHIT}"
    fi
} > "${REPORT}"

echo "Combined evaluation report: ${REPORT}"

# =============================================================================
# COMPLETION
# =============================================================================

echo ""
echo "======================================================"
echo " Assembly Evaluation Complete"
echo "======================================================"
echo ""
echo "Output files:"
echo "  TrinityStats (raw):       ${TRINITY_STATS_OUT}"
echo "  TrinityStats (clustered): ${CDHIT_STATS_OUT}"
echo "  seqkit stats:             ${SEQKIT_STATS_OUT}"
echo "  BUSCO (CD-HIT):           ${BUSCO_CDHIT_OUT}/"
echo "  BUSCO (Trinity):          ${BUSCO_TRINITY_OUT}/"
echo "  Combined report:          ${REPORT}"
echo ""
echo "Quality thresholds to check:"
echo "  [1] N50 > 1000 bp"
echo "  [2] Total genes/loci between 15,000 and 60,000"
echo "  [3] BUSCO complete (C) > 70% (adjusted for tissue-specific expression)"
echo "  [4] BUSCO fragmented (F) < 15%"
echo ""
echo "Next step: See 03_annotation/databases_setup.md to prepare annotation databases."
echo "           Then: bash 03_annotation/04_diamond_nr.sh"
