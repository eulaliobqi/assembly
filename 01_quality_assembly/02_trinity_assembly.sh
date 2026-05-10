#!/usr/bin/env bash
# =============================================================================
# Script: 02_trinity_assembly.sh
# Project: Mahanarva spectabilis Salivary Gland Transcriptome
# Purpose: De novo transcriptome assembly, redundancy removal, and ORF prediction
#
# Tools required (conda env: assembly):
#   - Trinity >= 2.15.1
#   - CD-HIT-EST >= 4.8.1
#   - TransDecoder >= 5.7.0
#   - seqkit >= 2.8.0
#
# Pipeline overview:
#   1. Trinity de novo assembly
#   2. CD-HIT-EST redundancy removal (clustering at 95% identity)
#   3. TransDecoder LongOrfs (identify candidate ORFs)
#   4. TransDecoder Predict (score and select final ORFs)
#
# Usage:
#   bash 01_quality_assembly/02_trinity_assembly.sh
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

# Input trimmed reads (output of 01_qc_trimming.sh)
SAMPLE="mahanarva_salivary_gland"
TRIMMED_R1="data/trimmed/${SAMPLE}_R1_trimmed.fastq.gz"
TRIMMED_R2="data/trimmed/${SAMPLE}_R2_trimmed.fastq.gz"

# Output directories
TRINITY_OUT="results/trinity_out"
ASSEMBLY_OUT="results/assembly"

# =============================================================================
# ASSEMBLY PARAMETERS
# Rationale for Hemiptera / salivary gland transcriptomics noted per parameter
# =============================================================================

# Parallelism
THREADS=16           # Use all available CPU cores; Trinity benefits from high thread count

# Memory allocation for Trinity
MEM="64G"            # 64 GB RAM recommended for moderate-complexity transcriptomes
                     # Increase to 128G if Trinity fails with memory errors on large datasets

# Minimum contig length
MIN_LENGTH=300       # Exclude contigs < 300 bp; reduces fragmentation noise
                     # Hemipteran transcripts often span 300-3000 bp coding sequences

# CD-HIT-EST clustering parameters
CDHIT_IDENTITY=0.95  # Cluster at 95% nucleotide identity to collapse near-identical isoforms
                     # A stricter threshold (e.g., 0.90) would be more aggressive
CDHIT_WORD=8         # Word size; 8 is optimal for identity >= 0.90 per CD-HIT documentation

# TransDecoder parameters
MIN_ORF_LENGTH=100   # Minimum ORF length in amino acids (default: 100)
                     # Increase to 150 for stricter filtering; 100 captures small secreted peptides
                     # relevant for salivary effectors in Hemiptera

# =============================================================================
# SETUP
# =============================================================================

echo "======================================================"
echo " Setup: Creating output directories"
echo "======================================================"

mkdir -p "${TRINITY_OUT}"
mkdir -p "${ASSEMBLY_OUT}"
mkdir -p "results/transdecoder"

echo "Trimmed R1: ${TRIMMED_R1}"
echo "Trimmed R2: ${TRIMMED_R2}"
echo "Trinity output: ${TRINITY_OUT}"

# =============================================================================
# STEP 1: Trinity de novo assembly
#
# Parameter rationale:
#   --seqType fq              : Input reads are FASTQ format
#   --left / --right          : Paired-end read files (R1 / R2)
#   --SS_lib_type RF          : Strand-specific library; RF = reverse-forward (dUTP method)
#                               Most common for Illumina strand-specific RNA-seq.
#                               Verify with library prep protocol; use FR for forward-stranded.
#   --min_kmer_cov 2          : Minimum k-mer coverage to include in assembly graph.
#                               Value of 2 reduces noise from sequencing errors while retaining
#                               transcripts with moderate expression (important for salivary gland,
#                               where some genes are lowly expressed).
#   --min_contig_length 300   : Discard assembled contigs shorter than 300 bp (reduces noise)
#   --jaccard_clip            : Recommended for gene-dense transcriptomes and for organisms
#                               where alternative splicing may produce chimeric contigs.
#                               Particularly important for insect transcriptomes.
#   --max_memory              : Maximum RAM for Trinity; must match available system memory
#   --CPU                     : Number of parallel threads
#   --output                  : Output directory for Trinity intermediate and final files
# =============================================================================

echo ""
echo "======================================================"
echo " Step 1/4: Trinity de novo assembly"
echo "======================================================"
echo "Parameters: threads=${THREADS}, memory=${MEM}, min_length=${MIN_LENGTH}"
echo "Library type: RF (reverse-forward, strand-specific)"

Trinity \
    --seqType fq \
    --left "${TRIMMED_R1}" \
    --right "${TRIMMED_R2}" \
    --SS_lib_type RF \
    --min_kmer_cov 2 \
    --min_contig_length "${MIN_LENGTH}" \
    --jaccard_clip \
    --max_memory "${MEM}" \
    --CPU "${THREADS}" \
    --output "${TRINITY_OUT}"

# Trinity output file
TRINITY_FASTA="${TRINITY_OUT}/Trinity.fasta"

echo ""
echo "Trinity assembly complete."
echo "Raw assembly: ${TRINITY_FASTA}"

# Quick stats on raw assembly
echo ""
echo "--- Raw assembly statistics ---"
seqkit stats \
    --all \
    --tabular \
    "${TRINITY_FASTA}"

# =============================================================================
# STEP 2: CD-HIT-EST redundancy removal
#
# Trinity often produces highly similar transcript isoforms. CD-HIT-EST clusters
# sequences at a defined nucleotide identity threshold and retains one representative
# per cluster, substantially reducing database size and downstream redundancy.
#
# Parameter rationale:
#   -c 0.95    : Cluster transcripts sharing >= 95% identity over the shorter sequence
#   -n 8       : Word size 8 (required for c >= 0.90 per CD-HIT guidelines)
#   -T         : Threads
#   -M         : Memory limit in MB (0 = no limit)
#   -d 0       : No length limit on description line in output FASTA headers
# =============================================================================

echo ""
echo "======================================================"
echo " Step 2/4: CD-HIT-EST redundancy removal"
echo "======================================================"
echo "Identity threshold: ${CDHIT_IDENTITY} | Word size: ${CDHIT_WORD}"

CDHIT_OUT="${ASSEMBLY_OUT}/${SAMPLE}_cdhit95.fasta"

cd-hit-est \
    -i "${TRINITY_FASTA}" \
    -o "${CDHIT_OUT}" \
    -c "${CDHIT_IDENTITY}" \
    -n "${CDHIT_WORD}" \
    -T "${THREADS}" \
    -M 0 \
    -d 0

echo "CD-HIT-EST complete."
echo "Clustered assembly: ${CDHIT_OUT}"

# Stats after clustering
echo ""
echo "--- Post-clustering assembly statistics ---"
seqkit stats \
    --all \
    --tabular \
    "${CDHIT_OUT}"

# =============================================================================
# STEP 3: TransDecoder - Identify candidate ORFs (LongOrfs)
#
# TransDecoder extracts Open Reading Frames (ORFs) from transcripts and scores
# them as likely coding or non-coding using a log-likelihood model.
#
# LongOrfs step:
#   -t                     : Input transcript FASTA
#   -m ${MIN_ORF_LENGTH}   : Minimum ORF length in amino acids
#   --output_dir           : Directory for TransDecoder output files
#
# Note for salivary gland / effector research:
#   A MIN_ORF_LENGTH of 100 aa (300 bp) is appropriate to capture small secreted
#   peptides that may function as effectors in host-plant interaction, which are
#   common in Hemiptera salivary glands.
# =============================================================================

echo ""
echo "======================================================"
echo " Step 3/4: TransDecoder LongOrfs - Candidate ORF identification"
echo "======================================================"
echo "Minimum ORF length: ${MIN_ORF_LENGTH} aa"

TRANSDECODER_DIR="results/transdecoder"

TransDecoder.LongOrfs \
    -t "${CDHIT_OUT}" \
    -m "${MIN_ORF_LENGTH}" \
    --output_dir "${TRANSDECODER_DIR}"

echo "TransDecoder LongOrfs complete."
echo "Candidate ORFs saved to: ${TRANSDECODER_DIR}"

# =============================================================================
# STEP 4: TransDecoder - Score and predict final ORFs (Predict)
#
# The Predict step uses a Markov model trained on the longest ORFs to score
# all candidates and select those most likely to represent genuine coding sequences.
#
# --output_dir              : Same directory as LongOrfs output
# --single_best_only        : Retain only the best-scoring ORF per transcript
#                             (recommended to avoid redundant entries downstream)
# -t                        : Input transcript FASTA (same as LongOrfs)
# =============================================================================

echo ""
echo "======================================================"
echo " Step 4/4: TransDecoder Predict - Final ORF selection"
echo "======================================================"

TransDecoder.Predict \
    -t "${CDHIT_OUT}" \
    --output_dir "${TRANSDECODER_DIR}" \
    --single_best_only

echo "TransDecoder Predict complete."

# Copy final protein sequences to assembly results directory
PROTEIN_OUT="${ASSEMBLY_OUT}/${SAMPLE}_transdecoder.pep"
cp "${CDHIT_OUT}.transdecoder.pep" "${PROTEIN_OUT}"

echo "Final protein sequences: ${PROTEIN_OUT}"

# =============================================================================
# FINAL ASSEMBLY STATISTICS
# =============================================================================

echo ""
echo "======================================================"
echo " Assembly Summary Statistics"
echo "======================================================"

echo ""
echo "--- Trinity raw assembly ---"
seqkit stats --all --tabular "${TRINITY_FASTA}"

echo ""
echo "--- After CD-HIT-EST (95% identity clustering) ---"
seqkit stats --all --tabular "${CDHIT_OUT}"

echo ""
echo "--- TransDecoder predicted proteins ---"
seqkit stats --all --tabular "${PROTEIN_OUT}"

echo ""
echo "--- Transcript length distribution (>= 300 bp) ---"
seqkit seq \
    --min-len "${MIN_LENGTH}" \
    "${CDHIT_OUT}" | seqkit stats --all --tabular

# =============================================================================
# COMPLETION
# =============================================================================

echo ""
echo "======================================================"
echo " Trinity Assembly Pipeline Complete"
echo "======================================================"
echo ""
echo "Key output files:"
echo "  Raw Trinity assembly:    ${TRINITY_FASTA}"
echo "  Clustered transcripts:   ${CDHIT_OUT}"
echo "  Predicted proteins:      ${PROTEIN_OUT}"
echo "  TransDecoder files:      ${TRANSDECODER_DIR}/"
echo ""
echo "Next step: bash 02_assembly_evaluation/03_stats_busco.sh"
