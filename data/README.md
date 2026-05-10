# Data Directory / Diretorio de Dados

This directory contains the input sequence data used in the functional annotation pipeline for the *Mahanarva spectabilis* salivary gland transcriptome project.

---

## Primary Input File

### `gland-saliv-cigarr.fa`

| Attribute | Value |
|-----------|-------|
| Description | Protein sequences predicted by TransDecoder from the Trinity de novo assembly of *Mahanarva spectabilis* salivary gland RNA-seq data |
| Organism | *Mahanarva spectabilis* (sugarcane spittlebug; Hemiptera: Cercopidae) |
| Tissue | Salivary gland |
| Format | FASTA (protein sequences, amino acids) |
| Number of sequences | 12,445 |
| Source | TransDecoder v5.7.0, `--single_best_only` mode applied to Trinity + CD-HIT-EST assembly |

### FASTA header format

Sequence headers follow the Trinity/TransDecoder naming convention:

```
>TRINITY_DN{locus}_c{component}_g{gene}_i{isoform}.p{orf}
```

Example:

```
>TRINITY_DN1234_c0_g1_i1.p1
>TRINITY_DN5678_c1_g2_i3.p2
```

Field descriptions:
- `TRINITY_DN{n}` - Trinity de novo locus identifier
- `c{n}` - Component (subgraph) within the locus
- `g{n}` - Gene model within the component
- `i{n}` - Isoform number
- `p{n}` - ORF number predicted by TransDecoder (`.p1` = best-scoring ORF per transcript when `--single_best_only` is used)

---

## Raw RNA-seq Data

The raw paired-end RNA-seq FASTQ files used to generate this assembly are **not included** in this repository due to their large size (typically 10-30 GB per paired-end sample in compressed format).

Raw sequencing data should be deposited in a public repository (e.g., NCBI SRA) upon publication. Accession numbers will be added here when available.

To reproduce the assembly from raw reads, follow the pipeline steps beginning with:

```bash
bash 01_quality_assembly/01_qc_trimming.sh
bash 01_quality_assembly/02_trinity_assembly.sh
```

Refer to `README.md` in the repository root for the full pipeline documentation.

---

## Data Provenance

1. Raw RNA-seq reads were quality-controlled using FastQC and fastp (Q20 filter, minimum length 50 bp, paired-end adapter auto-detection).
2. Trimmed reads were assembled de novo using Trinity with strand-specific parameters (`--SS_lib_type RF`, `--min_kmer_cov 2`, `--jaccard_clip`).
3. Trinity transcripts were clustered using CD-HIT-EST at 95% nucleotide identity to reduce redundancy.
4. Open Reading Frames (ORFs) were predicted using TransDecoder with a minimum length of 100 amino acids and `--single_best_only` to retain one protein per transcript.
5. The resulting protein FASTA file (`gland-saliv-cigarr.fa`) serves as the input for all downstream annotation steps.
