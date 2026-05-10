# Mahanarva spectabilis Salivary Gland Transcriptome: Assembly, Annotation and Functional Analysis

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Python%20%7C%20Bash-green.svg)
![Organism](https://img.shields.io/badge/organism-Mahanarva%20spectabilis-orange.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

---

## Overview / Visao Geral

This repository contains the complete bioinformatics pipeline for de novo transcriptome assembly, evaluation, and functional annotation of the salivary gland of *Mahanarva spectabilis* (sugarcane spittlebug, Hemiptera: Cercopidae). As a non-model insect, no reference genome is available for this species; therefore, all analyses rely on reference-free (de novo) approaches.

The salivary gland was selected as the focal tissue because spittlebug saliva plays a central role in host plant interaction, stylet-guided feeding, and potentially in plant defense suppression. Characterizing the salivary transcriptome provides the first large-scale view of genes expressed in this tissue, enabling downstream functional genomics, candidate effector discovery, and comparative hemipteran biology.

RNA-seq reads were assembled using Trinity, annotated against multiple databases (NCBI NR, eggNOG, Pfam), and subjected to Gene Ontology (GO) and KEGG pathway enrichment analyses. All scripts are parameterized and commented for reproducibility.

---

## Repository Structure / Estrutura do Repositorio

```
trinity_maharnava/
|
|-- README.md                        # This file
|-- .gitignore                       # Files excluded from version control
|
|-- data/
|   |-- README.md                    # Description of input data
|   `-- gland-saliv-cigarr.fa        # TransDecoder protein sequences (12,445 seqs)
|
|-- 01_quality_assembly/
|   |-- 01_qc_trimming.sh            # FastQC + fastp QC and trimming
|   `-- 02_trinity_assembly.sh       # Trinity + CD-HIT-EST + TransDecoder
|
|-- 02_assembly_evaluation/
|   `-- 03_stats_busco.sh            # TrinityStats + seqkit + BUSCO
|
|-- 03_annotation/
|   |-- databases_setup.md           # Guide to download and build databases
|   |-- 04_diamond_nr.sh             # DIAMOND BLASTx against NCBI NR
|   |-- 05_eggnog_pfam.sh            # eggNOG-mapper + HMMER/Pfam
|   `-- 06_merge_annotations.py      # Merge all annotation sources into one table
|
|-- 04_functional_analysis/
|   |-- 07_go_analysis.py            # GO term parsing and enrichment
|   |-- 08_kegg_analysis.py          # KEGG pathway mapping
|   `-- 09_figures.py                # Publication-quality figure generation
|
|-- results/
|   |-- annotation_complete.tsv      # Final merged annotation table
|   |-- annotation_report.txt        # Summary statistics of annotation
|   |-- go_top20_biological_process.csv
|   |-- go_top20_molecular_function.csv
|   |-- go_top20_cellular_component.csv
|   `-- kegg_pathways.csv            # KEGG pathway counts
|
`-- figures/
    |-- go_bp_barplot.png
    |-- go_mf_barplot.png
    |-- go_cc_barplot.png
    |-- kegg_pathways_barplot.png
    `-- annotation_summary_pie.png
```

---

## Pipeline Workflow / Fluxo do Pipeline

The pipeline is organized into six sequential steps:

```
Step 1: Quality Control
  Raw FASTQ reads
      |
      v
  FastQC (raw) --> MultiQC report
      |
      v
  fastp (trimming: Q20, min_len=50, adapter auto-detection)
      |
      v
  FastQC (trimmed) --> MultiQC report

Step 2: De Novo Assembly
  Trimmed reads
      |
      v
  Trinity (--SS_lib_type RF, --min_kmer_cov 2, --jaccard_clip)
      |
      v
  CD-HIT-EST (redundancy removal, identity=0.95)
      |
      v
  TransDecoder (ORF prediction: LongOrfs + Predict)

Step 3: Assembly Evaluation
  Trinity transcripts
      |
      v
  TrinityStats.pl (N50, contig counts)
      |
      v
  seqkit stats (>=300 bp filter)
      |
      v
  BUSCO (insecta_odb10, transcriptome mode)

Step 4: Functional Annotation
  TransDecoder protein sequences
      |
      +-- DIAMOND BLASTx vs NCBI NR (--evalue 1e-5, --max-target-seqs 1)
      |
      +-- eggNOG-mapper (GO terms, KEGG orthologs, COG categories)
      |
      `-- HMMER / Pfam-A (domain annotation)

Step 5: GO and KEGG Analysis
  Merged annotation table
      |
      +-- GO term frequency (Biological Process, Molecular Function, Cellular Component)
      |
      `-- KEGG pathway mapping via KEGG REST API

Step 6: Figure Generation
  Analysis results
      |
      v
  Horizontal barplots (top 20 GO terms per category)
  Barplot (top KEGG pathways)
  Pie chart (annotation source coverage)
```

---

## Dependencies and Environments / Dependencias e Ambientes

Two separate conda environments are used to avoid dependency conflicts.

### Environment 1: `assembly`

Used for steps 1-3 (QC, assembly, evaluation).

```bash
conda create -n assembly -c bioconda -c conda-forge \
    fastqc multiqc fastp trinity cd-hit transdecoder \
    seqkit busco
conda activate assembly
```

Key tool versions tested:
- Trinity >= 2.15.1
- fastp >= 0.23.4
- BUSCO >= 5.7.0
- CD-HIT >= 4.8.1
- TransDecoder >= 5.7.0
- seqkit >= 2.8.0

### Environment 2: `annotation`

Used for steps 4-6 (annotation and functional analysis).

```bash
conda create -n annotation -c bioconda -c conda-forge \
    diamond hmmer eggnog-mapper taxonkit \
    python=3.10 pandas matplotlib seaborn biopython requests
conda activate annotation
```

Key tool versions tested:
- DIAMOND >= 2.1.9
- HMMER >= 3.4
- eggNOG-mapper >= 2.1.12
- taxonkit >= 0.17.0
- Python >= 3.10

---

## Usage / Como Usar

All scripts should be run from the repository root directory. Adjust path variables at the top of each script before execution.

### Step 1: Quality Control and Trimming

```bash
conda activate assembly
bash 01_quality_assembly/01_qc_trimming.sh
```

### Step 2: Trinity Assembly

```bash
conda activate assembly
bash 01_quality_assembly/02_trinity_assembly.sh
```

### Step 3: Assembly Evaluation

```bash
conda activate assembly
bash 02_assembly_evaluation/03_stats_busco.sh
```

### Step 4: Database Setup (one-time)

Follow the instructions in `03_annotation/databases_setup.md` to download and build all required databases before running annotation steps.

### Step 4b: DIAMOND NR Annotation

```bash
conda activate annotation
bash 03_annotation/04_diamond_nr.sh
```

### Step 4c: eggNOG and Pfam Annotation

```bash
conda activate annotation
bash 03_annotation/05_eggnog_pfam.sh
```

### Step 5: Merge Annotations

```bash
conda activate annotation
python 03_annotation/06_merge_annotations.py
```

### Step 6: GO and KEGG Analysis + Figures

```bash
conda activate annotation
python 04_functional_analysis/07_go_analysis.py
python 04_functional_analysis/08_kegg_analysis.py
python 04_functional_analysis/09_figures.py
```

---

## Outputs / Arquivos de Saida

| File | Description |
|------|-------------|
| `results/annotation_complete.tsv` | Full annotation table with all sources merged (one row per protein) |
| `results/annotation_report.txt` | Annotation coverage statistics per source |
| `results/go_top20_biological_process.csv` | Top 20 GO terms: Biological Process |
| `results/go_top20_molecular_function.csv` | Top 20 GO terms: Molecular Function |
| `results/go_top20_cellular_component.csv` | Top 20 GO terms: Cellular Component |
| `results/kegg_pathways.csv` | KEGG pathway frequencies |
| `figures/go_bp_barplot.png` | GO BP horizontal barplot |
| `figures/go_mf_barplot.png` | GO MF horizontal barplot |
| `figures/go_cc_barplot.png` | GO CC horizontal barplot |
| `figures/kegg_pathways_barplot.png` | KEGG pathway barplot |
| `figures/annotation_summary_pie.png` | Annotation source coverage pie chart |

---

## Key Results Summary

- Input proteins: 12,445 sequences predicted by TransDecoder from Trinity assembly
- DIAMOND NR annotation coverage: see `results/annotation_report.txt`
- eggNOG GO annotation coverage: see `results/annotation_report.txt`
- Pfam domain coverage: see `results/annotation_report.txt`
- BUSCO completeness: see `02_assembly_evaluation/` outputs

---

## Citation / Citacao

If you use this pipeline or data in your research, please cite:

> Santos, E. et al. (in preparation). De novo transcriptome assembly and functional annotation of the salivary gland of *Mahanarva spectabilis* (Hemiptera: Cercopidae).

Database citations:
- Trinity: Grabherr et al. (2011) *Nature Biotechnology* 29, 644-652.
- DIAMOND: Buchfink et al. (2021) *Nature Methods* 18, 366-368.
- eggNOG-mapper: Cantalapiedra et al. (2021) *Molecular Biology and Evolution* 38(12), 5825-5829.
- BUSCO: Manni et al. (2021) *Molecular Biology and Evolution* 38(10), 4647-4654.
- Pfam: Mistry et al. (2021) *Nucleic Acids Research* 49(D1), D412-D419.

---

## Acknowledgments / Agradecimentos

This work was carried out at Universidade Federal de Vicosa (UFV), Brazil. We thank the bioinformatics community for developing and maintaining the open-source tools used in this pipeline.

---

## Contact / Contato

**Eulalio Santos**
Universidade Federal de Vicosa (UFV)
eulalio.santos@ufv.br

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
