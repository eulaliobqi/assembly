# Mahanarva spectabilis Salivary Gland Transcriptome: Assembly, Annotation and Functional Analysis

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Python%20%7C%20Bash-green.svg)
![Organism](https://img.shields.io/badge/organism-Mahanarva%20spectabilis-orange.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

---

## Overview / Visao Geral

This repository contains the complete bioinformatics pipeline for de novo transcriptome assembly, evaluation, and functional annotation of the salivary gland of *Mahanarva spectabilis* (sugarcane/pasture spittlebug, Hemiptera: Cercopidae). As a non-model insect, no reference genome is available for this species; therefore, all analyses rely on reference-free (de novo) approaches.

The salivary gland was selected as the focal tissue because spittlebug saliva plays a central role in host plant interaction, stylet-guided feeding, and potentially in plant defense suppression. Characterizing the salivary transcriptome provides the first large-scale view of genes expressed in this tissue, enabling downstream functional genomics, candidate effector discovery, and comparative hemipteran biology.

RNA-seq reads were assembled using Trinity, annotated against multiple databases (NCBI NR, eggNOG, Pfam), and subjected to Gene Ontology (GO) and KEGG pathway enrichment analyses. All scripts are parameterized and commented for reproducibility.

**This README is a repository/reproducibility guide.** For the full manuscript-style writeup -- complete Methods with exact tool versions and parameters, Results with every figure and table, Discussion, Limitations, and a live per-module status table -- see [`artigo.md`](artigo.md) / `artigo.docx`.

---

## Biological Motivation / Motivacao Biologica

*Mahanarva spectabilis* is one of the main "cigarrinha-das-pastagens" (pasture spittlebug) pests of *Brachiaria*/*Urochloa* forage grasses in Brazil, causing the characteristic **"amarelao"** symptom: progressive chlorosis and drying of the leaves around feeding sites, which can devastate pasture stands (Hernandez et al. 2022, *Front. Sustain. Food Syst.* 6:891417). Unlike phloem-feeding leafhoppers ("hopperburn", e.g. *Empoasca*), spittlebugs are strictly **xylem feeders**, and the current agronomic consensus points to a phytotoxemia mechanism mediated by enzymatically active saliva injected directly into xylem vessels, rather than mechanical vascular blockage alone (Backus, Serrano & Ranger 2005, *Annu. Rev. Entomol.* 50:125-151).

No study has yet chemically identified "the" toxin responsible for amarelao. A research group at UFV (Departamento de Bioquimica e Biologia Molecular) has been characterizing salivary/foam proteins of *M. spectabilis* by proteomics (Monteiro 2019, MSc dissertation, UFV -- candidate effectors including long-chain fatty acids; Rinaldi 2021, MSc dissertation, UFV -- salivary toxin/foam components; Rinaldi et al. 2026, *Arch. Insect Biochem. Physiol.* -- nymphal foam proteins + AlphaFold modeling). This transcriptome is intended as a complementary, transcript-level resource for that same research question, adding two analytical angles not yet explored for this species:

1. **Candidate salivary effectors/toxins** (`06_effector_prioritization/`): cross-referencing predicted secreted proteins (SignalP+TMHMM) with functional categories reported as phytotoxic/defense-suppressing in other Hemiptera (venom-like proteases, salivary secreted peptides, laccases, mucins, Ca-binding/EF-hand proteins, phospholipases, cell-wall-degrading CAZymes), expression level (Salmon TPM), and overlap with the UFV group's proteomic findings.
2. **Endosymbionts, pathogen screening and full microbiome census** (`07_metagenomic_screen/`, `08_metagenomic_deep/`): spittlebugs (Cercopidae) are known to carry obligate nutritional endosymbionts -- classically *Candidatus* Sulcia muelleri plus a co-symbiont, either *Zinderia insecticola* or, in some lineages, a *Sodalis*-like replacement (McCutcheon & Moran 2007, *PNAS* 104:19392-19397; Bennett & Moran 2013, *Genome Biol. Evol.* 5:1675-1688; Koga & Moran 2014, *ISME J.* 8:1237-1249). Foieri et al. (2022, *Bull. Insectology*) confirmed *Sulcia* by 16S rRNA in three South American pasture spittlebugs closely related to *Mahanarva* (*Notozulia entreriana*, *Deois mourei*, *Deois knoblauchii*), making its presence in *M. spectabilis* highly expected and confirmed here (see Key Results). Because spittlebugs feed exclusively on xylem, *Xylella fastidiosa* was a mechanistically plausible candidate vector hypothesis; **a dedicated screening round (raw-read genome-wide mapping, full 540-hit Bacteria + 256-hit Fungi genus census, RdRp-domain-directed viral discovery, and a microbial toxin/virulence keyword search) directly tested and refuted this and related pathogen hypotheses** (Xylella, Aster Yellows phytoplasma, plant-infecting viruses, phytopathogenic fungi/bacteria toxins) -- see Key Results Summary and `artigo.md` Sections 3.3-3.4 and 4 for full detail. By elimination, this reinforces the salivary effector/toxin hypothesis (item 1 above) as the best-supported explanation for amarelao given current data.

---

## Repository Structure / Estrutura do Repositorio

Note: this tree reflects the actual repository contents, which diverged from the originally planned 6-step layout below (kept for historical reference) as the pipeline was consolidated and extended.

```
trinity_maharnava/
|
|-- README.md                        # This file
|-- artigo.md / artigo.docx          # Full manuscript-style writeup (methods incl. exact tool
|                                     # versions/parameters, results, figures, discussion,
|                                     # limitations, live analysis-status table) -- the primary,
|                                     # actively-maintained document; this README is a repo guide
|-- roteiro-apresentacao-minicurso.md/.docx  # Teaching walkthrough (assembly QC + annotation)
|-- scripts.md                       # Generic/commented reference version of the whole pipeline
|-- .gitignore                       # Files excluded from version control
|
|-- data/
|   |-- README.md                    # Description of input data (raw FASTQ not included)
|   |-- gland-saliv-cigarr.fa        # TransDecoder protein sequences (12,445 seqs)
|   `-- transdecoder/                # .pep/.cds/.gff3/.bed TransDecoder output
|
|-- 01_quality_assembly/             # FastQC + fastp + Trinity assembly scripts
|-- 02_assembly_evaluation/          # TrinityStats + seqkit + BUSCO (insecta_odb10)
|
|-- 03_annotation/
|   |-- auto_annotate.py             # DIAMOND NR + TaxonKit + eggNOG-mapper + HMMER/Pfam (single consolidated script)
|   |-- 07_fix_annotation_merge.py   # Standalone fix for the eggNOG/taxonomy merge bug (see Known Issues)
|   |-- 08_cazy_annotation.sh        # Dedicated dbCAN3 (run_dbcan) CAZyme annotation
|   |-- 09_merge_cazy.py             # Merges dbCAN calls into annotation_complete.tsv (cazy column)
|   `-- databases_setup.md           # Guide to download and build databases
|
|-- 04_functional_analysis/
|   |-- go_kegg_analysis.py          # GO term frequency + KEGG pathway mapping + figures (uses cache/ for OBO/KEGG API results)
|   |-- plot_annotation.py           # Publication-quality annotation summary figure
|   `-- plot_assembly_qc.py          # Assembly QC + ORF-type summary figure
|
|-- 05_secretome/
|   `-- secretome_predict.py         # TMbed classical secretome prediction (replaces SignalP6/TMHMM, see Known Issues)
|
|-- 06_effector_prioritization/
|   |-- effector_candidates.py       # Secretome x curated toxin/effector terms x TPM ranking
|   `-- plot_effectors.py            # Effector candidates dot-plot figure
|
|-- 07_metagenomic_screen/
|   |-- 01_taxonomic_summary.py      # Taxonomic distribution + Sulcia/Zinderia/Sodalis-like candidate extraction (Camada 1)
|   |-- 04_cross_validate_endosymbionts.py  # Camada 2: Whokaryote+Tiara structural cross-validation
|   |-- 09_plot_blobtools_gc_tpm.py  # Camada 3: GC%xTPM blob plot + Mann-Whitney test
|   |-- 10_plot_microbiome_census.py # Camada 3: full Bacteria+Fungi genus census figure
|   |-- 11_plot_pathogen_screening.py # Camada 3: viral reclassification + Xylella/phytoplasma coverage figure
|   `-- results/                     # Camada 3 (2026-07-25): see Known Issues -- underlying
|       |                            # mapping/hmmscan/keyword-search commands not yet scripted
|       |-- viral_discovery/         # RdRp HMM subset (31 Pfam families) + DIAMOND vs viral RefSeq
|       |-- pathogen_confirmation/   # Xylella/phytoplasma genome-wide read mapping (REFUTED)
|       |-- fungal_breakdown/        # Full 256-hit Fungi genus census
|       |-- full_microbiome_census/  # Full 540-hit Bacteria genus census + toxin keyword search
|       |-- blobtools_gc_tpm/        # GC% x TPM per-contig table + plot (Sulcia AT-richness confirmation)
|       `-- completeness_checklist/  # Informal Sulcia gene-content checklist (NOT a CheckM2 equivalent)
|
|-- 08_metagenomic_deep/
|   |-- 02_plot_groel_phylogeny.py   # GroEL ML tree figure (IQ-TREE output)
|   `-- results/phylogenetics/       # GroEL ML tree (Sulcia refs + Sodalis/Bacteroidetes outgroup) -- INCONCLUSIVE (bootstrap 49-72%, below 95% criterion)
|
|-- results/
|   |-- annotation_complete.tsv      # Final merged annotation table (incl. dbCAN-derived cazy column)
|   |-- annotation_report.txt        # Summary statistics of annotation
|   |-- taxon_lineage.tsv            # taxid -> full/reformatted NCBI lineage lookup (not versioned, see .gitignore)
|   |-- cazy/overview.tsv            # Dedicated dbCAN3 CAZyme calls (DIAMOND + dbCAN-HMM + dbCAN-sub)
|   |-- secretome/                   # TMbed classical secretome (secretome_classical.tsv, secretome_report.txt)
|   |-- effector_candidates/         # effector_candidates_ranked.tsv + report
|   |-- endosymbiont_candidates/     # Sulcia/Sodalis-like hits + Xylella/phytoplasma leads (now refuted, see 07_metagenomic_screen/results/pathogen_confirmation/)
|   |-- whokaryote/                  # Camada 2 per-contig eukaryote/prokaryote calls
|   |-- go/                          # go_top20_{BP,CC,MF}.csv
|   `-- kegg/                        # kegg_pathways.csv
|
|-- expression/
|   |-- salmon-quant.sf              # Salmon transcript-level quantification (TPM)
|   `-- expressed_transcripts.txt
|
|-- environment/
|   |-- env_annotation.yml           # diamond/taxonkit/eggnog-mapper/hmmer, python=3.11 (env name: auto_annotate)
|   |-- env_secretome.yml            # TMbed (torch/transformers<5), python=3.11 -- isolated, see Known Issues
|   |-- env_cazy.yml                 # dbcan (run_dbcan / dbCAN3)
|   `-- env_metagenome.yml           # whokaryote + tiara -- isolated (old numpy/sklearn/Python 3.8 stack)
|
`-- figures/                         # All PNG (300 dpi, publication-ready) + TIFF (archival, gitignored)
    |-- assembly_qc_summary.png
    |-- annotation_summary.png
    |-- go_distribution.png
    |-- kegg_pathways_{bar,bubble}.png
    |-- secretome_summary.png
    |-- effector_candidates.png
    |-- microbiome_census.png
    |-- pathogen_screening.png
    |-- blobplot_gc_tpm.png
    `-- groel_phylogeny.png
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

Step 7: Classical Secretome Prediction (05_secretome/, done)
  TransDecoder proteins
      |
      `-- TMbed (Bernhofer & Rost 2022): signal peptide + TM segment
          prediction in a single protein-language-model pass -- replaces
          SignalP6/TMHMM, whose DTU academic-license tarball was never
          obtained in this or two other lab projects (see Known Issues)
      |
      `-- Filter: signal peptide present AND <=1 TM segment --> classical secretome

Step 8: Candidate Effector/Toxin Prioritization (06_effector_prioritization/, done)
  Classical secretome + annotation_complete.tsv (incl. dedicated dbCAN CAZy
  calls, step 8b) + Salmon TPM
      |
      `-- Rank by: secreted status, curated toxin/effector term & domain list,
          expression level, overlap with UFV proteomics (Monteiro 2019; Rinaldi 2021, 2026)

Step 8b: Dedicated dbCAN CAZyme Annotation (03_annotation/08_cazy_annotation.sh, done)
  TransDecoder proteins
      |
      `-- run_dbcan (DIAMOND + dbCAN-HMM + dbCAN-sub) against the real
          dbCAN database -- replaces the low-sensitivity eggNOG-derived
          CAZy column (1.4%/175 proteins, 0 GH28/GH5 hits)

Step 9: Endosymbiont / Microbial Screening (07_metagenomic_screen/, done)
  annotation_complete.tsv taxonomic flags + taxon_lineage.tsv
      |
      +-- Layer 1: DIAMOND/lineage-based candidate extraction (01_taxonomic_summary.py)
      |
      `-- Layer 2: Whokaryote+Tiara structural eukaryote/prokaryote
          classification of assembled contigs, cross-validated against
          Layer 1 (04_cross_validate_endosymbionts.py)

Step 10: Pathogen Screening / Full Microbiome Census (Camada 3, done 2026-07-25)
  Raw FASTQ (gland-saliv_{1,2}.fq.gz, 86.7M read pairs) + assembled contigs
  + annotation_complete.tsv, executed via direct commands during the
  analysis session (not standalone numbered scripts, unlike steps 1-9 --
  see Known Issues)
      |
      +-- Full genus-level census of ALL 540 Bacteria + 256 Fungi hits
      |   (not just the pre-selected candidates from Layer 1)
      |
      +-- Viral discovery: 31 RdRp Pfam HMM families (hmmfetch from the
      |   locally installed Pfam-A.hmm) x hmmscan on TransDecoder proteins,
      |   + DIAMOND blastx of contigs vs NCBI RefSeq viral (722,107 seqs);
      |   cross-referenced against the original 30 DIAMOND/NR virus hits,
      |   10 of which were reclassified as Metaviridae/Eupolintoviridae
      |   (host-genome retrotransposon-like elements, not infectious virus)
      |
      +-- Xylella fastidiosa / Aster Yellows phytoplasma: genome-wide
      |   bowtie2 mapping of raw reads against real NCBI reference genomes,
      |   breadth/depth of coverage computed, covered positions checked
      |   against real GFF3 gene coordinates -- REFUTED (both leads)
      |
      +-- Toxin/virulence keyword search across all Bacteria+Fungi hits
      |   (diamond_title/eggnog_desc/pfam_domains), independent of organism
      |
      `-- GroEL maximum-likelihood phylogeny (Sulcia refs + Sodalis/
          Bacteroidetes outgroup, IQ-TREE ultrafast bootstrap) -- INCONCLUSIVE
```

---

## Dependencies and Environments / Dependencias e Ambientes

Five separate conda environments are used to avoid dependency conflicts. **Exact versions below are the ones actually run to produce every result in this repo and in `artigo.md`** (verified via `conda list` on the analysis server, not just pinned as minimums -- see the integrity audit in Known Issues), not aspirational minimums.

### Environment 1: `assembly`

Used for steps 1-3 (QC, assembly, evaluation) plus Salmon quantification and the Camada 3 Bowtie2 mapping.

```bash
conda create -n assembly -c bioconda -c conda-forge \
    fastqc=0.12.1 multiqc=1.21 fastp=0.23.4 trinity=2.15.2 \
    cd-hit=4.8.1 seqkit=2.13.0 bowtie2=2.5.5 salmon=1.10.3
conda activate assembly
```

TransDecoder and BUSCO are kept in their own environments on the analysis server (`orf_prediction`: TransDecoder 5.7.1; `busco`: BUSCO 6.0.0) to avoid dependency conflicts with Trinity's own bundled toolchain -- create separately if reproducing exactly:

```bash
conda create -n orf_prediction -c bioconda -c conda-forge transdecoder=5.7.1
conda create -n busco -c bioconda -c conda-forge busco=6.0.0
```

### Environment 2: `auto_annotate` (see `environment/env_annotation.yml`)

Used for step 4 (functional annotation, `03_annotation/auto_annotate.py`) and the Camada 3 RdRp/viral DIAMOND+HMMER steps.

```bash
conda env create -f environment/env_annotation.yml
conda activate auto_annotate
```

Exact versions: DIAMOND 2.1.9, HMMER 3.4, eggNOG-mapper 2.1.12, TaxonKit 0.15.1, Python 3.11. (dbCAN's own DIAMOND, in the `cazy` environment below, is a newer 2.2.4 -- kept separate deliberately, not a version drift bug.)

### Environment 3: `secretome` (see `environment/env_secretome.yml`)

Used for step 7 (classical secretome prediction, TMbed 1.0.2). Kept isolated from `auto_annotate` because it pins its own PyTorch/transformers stack (exact versions run: torch 2.13.0, transformers 4.57.6).

```bash
conda env create -f environment/env_secretome.yml
conda activate secretome
```

`transformers` is pinned `<5`: TMbed's `embed.py` calls the `tokenizer.batch_encode_plus()` API, removed in transformers v5's tokenization overhaul (still present, deprecated, throughout the v4 line). `tiktoken`/`protobuf` are required by transformers' tokenizer-loading fallback path even though TMbed only needs the plain SentencePiece-based `T5Tokenizer`.

### Environment 4: `cazy` (see `environment/env_cazy.yml`)

Used for step 8b (dedicated dbCAN3 CAZyme annotation). Exact versions run: `run_dbcan` 5.2.9, DIAMOND 2.2.4 (bundled dependency, distinct from the 2.1.9 in `auto_annotate`), pyhmmer 0.12.1.

```bash
conda env create -f environment/env_cazy.yml
conda activate cazy
run_dbcan database --no-cgc --db_dir /path/to/dbcan_db   # one-time, ~7.7 GB
```

### Environment 5: `metagenome` (see `environment/env_metagenome.yml`)

Used for step 9 Layer 2 (Whokaryote+Tiara). Kept isolated because `whokaryote` pins an old numpy/scikit-learn/Python 3.8 stack. Exact versions run: Whokaryote 1.1.2, Tiara 1.0.3.

```bash
conda env create -f environment/env_metagenome.yml
conda activate metagenome
```

### Environment 6: `phylo` (GroEL phylogeny, `08_metagenomic_deep/`)

Not shipped as a repo `environment/*.yml` (single-tool, ad hoc analysis) -- IQ-TREE 3.1.1 was the exact version run (ModelFinder + 1000-replicate ultrafast bootstrap).

```bash
conda create -n phylo -c bioconda -c conda-forge iqtree=3.1.1
```

---

## Usage / Como Usar

All scripts should be run from the repository root directory unless noted. Adjust path variables at the top of each script before execution. This mirrors the actual scripts committed to the repo -- for a generic, teaching-oriented walkthrough of the underlying commands, see `scripts.md`; for full parameters/versions/rationale, see `artigo.md` Section 2.

### Steps 1-3: QC, Assembly, Evaluation

```bash
conda activate assembly
bash 01_quality_assembly/01_qc_trimming.sh
bash 01_quality_assembly/02_trinity_assembly.sh   # Trinity -> CD-HIT-EST -> TransDecoder
bash 02_assembly_evaluation/03_stats_busco.sh     # TrinityStats.pl + seqkit + BUSCO
```

### Step 4: Database Setup (one-time)

Follow `03_annotation/databases_setup.md` to download and build the NCBI NR DIAMOND database, eggNOG-mapper databases, and Pfam-A before running annotation.

### Step 4b: Functional Annotation (DIAMOND + TaxonKit + eggNOG-mapper + Pfam)

```bash
conda activate auto_annotate
python 03_annotation/auto_annotate.py --input data/gland-saliv-cigarr.fa
# Resume after interruption: add --resume
# Run a single phase only: add --phase <phase_name>

# If reproducing from an older/out-of-sync run (see Known Issues, merge bug):
python 03_annotation/07_fix_annotation_merge.py
```

### Step 4c: GO/KEGG Analysis + Figures

```bash
conda activate auto_annotate   # needs pandas, matplotlib, requests
cd 04_functional_analysis
python go_kegg_analysis.py --emapper ../results/emapper.emapper.annotations
python plot_annotation.py
python plot_assembly_qc.py
```

### Step 5: Classical Secretome Prediction (TMbed)

```bash
conda activate secretome
python 05_secretome/secretome_predict.py
# Resume if TMbed already ran: --resume
```

### Step 6: Dedicated dbCAN3 CAZyme Annotation

```bash
conda activate cazy
bash 03_annotation/08_cazy_annotation.sh /path/to/dbcan_db_dir
python 03_annotation/09_merge_cazy.py    # merges dbCAN calls into annotation_complete.tsv
```

### Step 7: Endosymbiont Screening (Camadas 1-2)

```bash
conda activate auto_annotate
python 07_metagenomic_screen/01_taxonomic_summary.py           # Camada 1: DIAMOND/lineage extraction

conda activate metagenome
# Run Whokaryote + Tiara on the assembled contigs first (see tool docs), then:
python 07_metagenomic_screen/04_cross_validate_endosymbionts.py   # Camada 2: structural cross-validation
```

### Step 8: Candidate Effector/Toxin Prioritization

```bash
conda activate auto_annotate   # needs pandas
python 06_effector_prioritization/effector_candidates.py
python 06_effector_prioritization/plot_effectors.py
```

### Camada 3: Pathogen Screening / Full Microbiome Census / GroEL Phylogeny

The mapping, `hmmscan`/`blastx`, and keyword-search commands underlying this layer were run directly during the analysis session and are **not yet** committed as standalone scripts (see Known Issues) -- `artigo.md` Section 2.7 documents the exact commands/parameters/tool versions used. Once the result tables exist under `07_metagenomic_screen/results/` and `08_metagenomic_deep/results/`, the figures are regenerated with:

```bash
conda activate assembly   # needs pandas, matplotlib, scipy
python 07_metagenomic_screen/09_plot_blobtools_gc_tpm.py
python 07_metagenomic_screen/10_plot_microbiome_census.py
python 07_metagenomic_screen/11_plot_pathogen_screening.py
python 08_metagenomic_deep/02_plot_groel_phylogeny.py
```

---

## Outputs / Arquivos de Saida

| File | Description |
|------|-------------|
| `results/annotation_complete.tsv` | Full annotation table with all sources merged (one row per protein), incl. dbCAN `cazy` column |
| `results/annotation_report.txt` | Annotation coverage statistics per source |
| `results/go/go_top20_BP.csv`, `_MF.csv`, `_CC.csv` | Top 20 GO terms per category (Biological Process / Molecular Function / Cellular Component) |
| `results/kegg/kegg_pathways.csv` | KEGG pathway frequencies |
| `figures/assembly_qc_summary.png` | Assembly/ORF-type QC summary figure |
| `figures/annotation_summary.png` | Annotation source coverage + taxonomic origin figure |
| `figures/go_distribution.png` | Top 20 GO terms, 3-panel (BP/MF/CC) |
| `figures/kegg_pathways_bar.png`, `_bubble.png` | KEGG pathway bar chart / bubble chart |
| `results/secretome/secretome_classical.tsv` | Classical secretome (TMbed: signal peptide AND <=1 TM segment) |
| `figures/secretome_summary.png` | Secretome prediction 3-panel summary figure |
| `results/cazy/overview.tsv` | Dedicated dbCAN3 CAZyme calls (DIAMOND + dbCAN-HMM + dbCAN-sub) |
| `results/effector_candidates/effector_candidates_ranked.tsv` | Ranked candidate salivary effectors/toxins (35) |
| `figures/effector_candidates.png` | Effector candidates dot-plot (TPM x curated category) |
| `results/whokaryote/` | Camada 2 per-contig eukaryote/prokaryote calls (Whokaryote+Tiara) |
| `results/endosymbiont_candidates/endosymbionts_cross_validated.tsv` | Camada 1 x Camada 2 endosymbiont cross-validation |
| `07_metagenomic_screen/results/full_microbiome_census/`, `fungal_breakdown/` | Full 540-hit Bacteria + 256-hit Fungi genus census |
| `07_metagenomic_screen/results/viral_discovery/` | RdRp-directed viral discovery + reclassification of the original 30 DIAMOND/NR virus hits |
| `07_metagenomic_screen/results/pathogen_confirmation/` | Xylella/phytoplasma genome-wide coverage (REFUTED) |
| `figures/microbiome_census.png`, `pathogen_screening.png` | Camada 3 summary figures |
| `07_metagenomic_screen/results/blobtools_gc_tpm/` + `figures/blobplot_gc_tpm.png` | GC%xTPM per-contig table/plot + Mann-Whitney test |
| `08_metagenomic_deep/results/phylogenetics/` + `figures/groel_phylogeny.png` | GroEL ML phylogeny (IQ-TREE, inconclusive) |

---

## Key Results Summary

- Input proteins: 12,445 sequences predicted by TransDecoder from Trinity assembly (90,344 Trinity genes / 103,560 transcripts, N50=738)
- BUSCO completeness (insecta_odb10): C:96.2% [S:39.9%, D:56.3%], F:1.9%, M:1.9%, n=1367
- Annotation coverage (post merge-fix, see `results/annotation_report.txt`): 62.1% with Pfam domain, 44.0% with GO term, 42.6% with KEGG ortholog
- **Dedicated dbCAN CAZyme annotation** (step 8b, `results/cazy/overview.tsv`): 468 proteins (3.8%) with >=1 CAZy family call (DIAMOND + dbCAN-HMM + dbCAN-sub against the real dbCAN database) vs. 175 (1.4%) from the low-sensitivity eggNOG-derived column -- critically, **15 proteins carry a GH28 or GH5\* (cellulase/pectinase-like) family call**, where eggNOG had found zero; these are new candidates for cell-wall-degrading phytotoxic effectors, folded into the effector prioritization ranking (step 8)
- Taxonomic origin of best hits: 70.0% Eukaryota, 4.3% Bacteria, 2.1% Fungi (76.6% entomopathogenic overall -- dominant single genus is *Entomophthora* [96 hits], not *Metarhizium* [56 hits] as stated in an earlier version of this document), 0.2% Viruses, 25.4% unclassified -- see full genus-level census below
- **Classical secretome** (step 7, TMbed, `results/secretome/secretome_classical.tsv`): 1,171 proteins (9.4%) with signal peptide AND <=1 TM segment; 1,238 proteins (9.9%) have a signal peptide call overall
- **Candidate salivary effectors/toxins** (step 8, `results/effector_candidates/effector_candidates_ranked.tsv`): 35 proteins are both in the classical secretome AND match a curated toxin/effector term -- top hits include a salivary secreted protein (best DIAMOND hit: *Triatoma infestans*), a venom protease-like (best hit: *Macrosteles quadrilineatus*, a leafhopper), a venom serine carboxypeptidase, mucins, a venom dipeptidyl peptidase 4-like, and several EF-hand/Ca-binding proteins
- **Endosymbiont candidates** (`results/endosymbiont_candidates/sulcia_sodalis_hits.tsv`): 57 proteins matching *Candidatus* Karelsulcia muelleri (~99% identity, classic housekeeping genes: 6-phosphofructokinase, GAPDH, GroEL, malic enzyme, translation factor IF-2) + 1 protein matching a *Sodalis*-like symbiont of *Philaenus spumarius* -- consistent with the obligate dual endosymbiosis reported for spittlebugs (see Biological Motivation)
- **Endosymbiont Layer 2 cross-validation** (`results/endosymbiont_candidates/endosymbionts_cross_validated.tsv`): Whokaryote+Tiara's independent, structural (gene-content-based, not sequence-similarity-based) eukaryote/prokaryote classification of assembled contigs confirms 3/60 candidates as concordant (predicted prokaryote) and 0 as discordant; the remaining 57 could not be evaluated because Whokaryote only classifies contigs >=5000bp and most endosymbiont candidates are single genes on short Trinity transcripts -- a coverage limitation of Layer 2, not evidence against the Layer 1 calls
- **Endosymbiont Camada 3 evidence** (`07_metagenomic_screen/results/blobtools_gc_tpm/`, `08_metagenomic_deep/results/phylogenetics/`): GC% of the 37 Sulcia/Sodalis candidates with expression data (median 24.9%) is significantly lower than the rest of the annotated eukaryotic transcriptome (median 36.2%; Mann-Whitney p=8.1e-23), consistent with Sulcia's known AT-rich reduced genome. A GroEL maximum-likelihood phylogeny (Sulcia references + Sodalis/*Bacteroides fragilis* outgroup) was **inconclusive** -- the candidate did not nest within the Sulcia clade with adequate bootstrap support (49-72%, below the 95% threshold), reported as-is without further taxon resampling
- **Pathogen screening -- Xylella/phytoplasma REFUTED** (`07_metagenomic_screen/results/pathogen_confirmation/`): the 2 low-priority single-hit leads from earlier annotation (`results/endosymbiont_candidates/low_priority_pathogen_leads.tsv`) were directly tested by genome-wide bowtie2 mapping of the ~173M raw reads against real NCBI reference genomes (*X. fastidiosa* subsp. *multiplex* GCF_042238405.1; Aster Yellows phytoplasma NC_007716.1+plasmids). Both show breadth of coverage <0.3%, with 98-100% of the (very sparse) covered positions falling inside conserved 16S/23S rRNA operons -- the classic signature of non-specific cross-mapping, not real pathogen presence
- **Full microbiome census** (`07_metagenomic_screen/results/full_microbiome_census/`): all 540 Bacteria hits (not just pre-selected candidates) were grouped by genus. Notable finding: 88 hits (2nd-largest specific genus) to *Herbaspirillum*, a classic diazotrophic endophyte of tropical grasses **including *Brachiaria*/*Urochloa*, the exact host plant** -- not a pathogen, but evidence of plant-derived bacterial material captured via ingested xylem sap. All 256 Fungi hits were also grouped (76.6% entomopathogenic: *Entomophthora muscae*, *Metarhizium* spp., *Massospora cicadina*; *Fusarium* spp., 8 hits, is the only mechanistically plausible xylem-colonizing phytopathogen genus, but signal too weak to confirm)
- **Viral discovery and reconciliation** (`07_metagenomic_screen/results/viral_discovery/`): RdRp-domain-directed screening (31 Pfam families) + DIAMOND vs NCBI RefSeq viral confirmed 4 real viruses via 2 independent sources (domain + BLASTx identity) -- 3 with high confidence (Jingmenvirus-like/*Wuhan flea virus*, Nodaviridae-like/*Boolarra virus*, Dicistroviridae-like/*Drosophila C virus*-*Nilaparvata lugens C virus*) and 1 with medium-high confidence (Cypovirus-like: strong RdRp domain, but low/divergent sequence identity, 26.3%) -- all arthropod-specific lineages with no plant-pathogenicity precedent. Directed search for the Phytoreovirus RdRp family (PF27669) -- the classic Auchenorrhyncha-vectored plant virus group -- found **zero hits**. Cross-referencing against the original 30 DIAMOND/NR virus-flagged proteins revealed that 10 (`Halyomorpha halys erranti-like virus 1`) are actually Metaviridae (host-genome LTR retrotransposons, not infectious virus) and 2 more are Eupolintoviridae (Polinton-like elements) -- verified via live NCBI taxonomy lookup
- **Microbial toxin/virulence keyword search**: no classical phytotoxin gene (coronatine, tabtoxin, syringomycin, NEP1-like necrosis-inducing proteins) found among Bacteria+Fungi hits; only universal bacterial toxin-antitoxin systems (RelE/RelB, VapBC, MazF -- persistence/stress regulation, unrelated to virulence) and one *Metarhizium* phospholipase (consistent with its known entomopathogenic, not phytopathogenic, role)

### Known Issues / Problemas Conhecidos

**A full integrity audit (2026-08-30/31)** independently recomputed virtually every number in this README/`artigo.md` from raw source files on both the analysis server and this repo, and checksummed server<->local result files -- **nothing was found fabricated**. It did find and fix two real bugs in `03_annotation/09_merge_cazy.py` (a substring-match bug that mis-counted GH28/GH5 CAZy hits as 16 instead of 15, and a merge step that left 574 stale eggNOG `cazy` values instead of cleanly overwriting with the 468 dbCAN-confirmed calls) and one latent low-severity bug in `06_effector_prioritization/effector_candidates.py` (a GH28/GH5 regex that didn't match dbCAN's underscore subfamily suffixes, e.g. `GH5_12` -- zero impact on the published 35 effector candidates). See `artigo.md` Section 6, items 17-18 for the full account.

The `annotation_complete.tsv` shipped in earlier commits had a stale merge (empty GO/KEGG/eggNOG-OG/COG columns; `is_fungi`/`is_eukaryote` flags always 0) because it had been generated by an older, out-of-sync version of the annotation script. This was diagnosed and fixed by `03_annotation/07_fix_annotation_merge.py`, which re-derives these fields directly from the raw `emapper.emapper.annotations` (matched by real header, not hardcoded column indices) and from the full (non-reformatted) NCBI lineage in `results/taxon_lineage.tsv`. The corresponding index bug in `auto_annotate.py::_parse_emapper` (`eggnog_og` read from the wrong column) was also patched so that future from-scratch runs do not reintroduce it. Post-fix counts were cross-checked against a prior known-good run hardcoded in `04_functional_analysis/plot_annotation.py` (Bacteria, Fungi, Viruses and Pfam counts matched exactly).

**Camada 3 (pathogen screening/full microbiome census, 2026-07-25) was executed via direct commands during the analysis session, not as standalone numbered scripts** like steps 1-9 -- a departure from this repo's usual convention. This is a known reproducibility gap: the exact commands are documented in the project's session memory but not committed as reusable `.py`/`.sh` files in `07_metagenomic_screen/`/`08_metagenomic_deep/`. A 4th screening layer (CAT/BAT, contig-level taxonomic classification without Whokaryote's 5000bp minimum size cutoff) was designed but not executed -- the required database was confirmed at 91.6GB (GTDB) to 197.5GB (NCBI nr), judged disproportionate to the expected gain given shared server disk space; deferred as optional future work.

**SignalP6/TMHMM were never installed** in this or two other lab projects (`RLPredictiOme/`, `caracterization-trypsin/`) because both tools require a DTU academic-license tarball download that was never completed, and neither is available on bioconda/conda-forge under any version. Step 7 was re-implemented around **TMbed** (Bernhofer & Rost 2022, *BMC Bioinformatics*), a pip-installable, fully local, no-login protein-language-model predictor that classifies signal peptide and TM helix/strand in one pass. Getting it running surfaced three real, unrelated dependency incompatibilities between TMbed's 2022-era code and the current (2026) package ecosystem, each fixed and pinned in `environment/env_secretome.yml`: (1) the latest `transformers` (v5) removed the `tokenizer.batch_encode_plus()` API TMbed's `embed.py` calls -- pinned `transformers<5`; (2) transformers' tokenizer-loading fallback path additionally requires `tiktoken` and `protobuf` even though the model only uses a plain SentencePiece `T5Tokenizer`; (3) a bundled/partial local model cache directory inside the installed `tmbed` package (missing `spiece.model`) caused an unrelated-looking `AttributeError`/`ValueError` chain until cleared, forcing a fresh download from the `Rostlab/prot_t5_xl_half_uniref50-enc` HuggingFace repo.

---

## Citation / Citacao

If you use this pipeline or data in your research, please cite:

> Santos, E. et al. (in preparation). De novo transcriptome assembly and functional annotation of the salivary gland of *Mahanarva spectabilis* (Hemiptera: Cercopidae).

Database/tool citations (full table with exact versions run in `artigo.md` Section 2.9):
- Trinity: Grabherr et al. (2011) *Nature Biotechnology* 29, 644-652; Haas et al. (2013) *Nature Protocols* 8(8), 1494-1512 (also covers TransDecoder).
- FastQC: Andrews, S. (2010). Babraham Bioinformatics.
- fastp: Chen, S. et al. (2018) *Bioinformatics* 34(17), i884-i890.
- MultiQC: Ewels, P. et al. (2016) *Bioinformatics* 32(19), 3047-3048.
- CD-HIT: Fu, L. et al. (2012) *Bioinformatics* 28(23), 3150-3152.
- seqkit: Shen, W. et al. (2016) *PLOS ONE* 11(10), e0163962.
- DIAMOND: Buchfink et al. (2021) *Nature Methods* 18, 366-368.
- TaxonKit: Shen, W. & Ren, H. (2021) *Journal of Genetics and Genomics* 48(9), 844-850.
- eggNOG-mapper: Cantalapiedra et al. (2021) *Molecular Biology and Evolution* 38(12), 5825-5829.
- HMMER: Eddy, S.R. (2011) *PLOS Computational Biology* 7(10), e1002195.
- BUSCO: Manni et al. (2021) *Molecular Biology and Evolution* 38(10), 4647-4654.
- Pfam: Mistry et al. (2021) *Nucleic Acids Research* 49(D1), D412-D419.
- Salmon: Patro, R. et al. (2017) *Nature Methods* 14(4), 417-419.
- TMbed: Bernhofer, M. & Rost, B. (2022). TMbed: transmembrane proteins predicted through language model embeddings. *BMC Bioinformatics* 23, 326.
- dbCAN: Zheng, J. et al. (2023). dbCAN3: automated carbohydrate-active enzyme and substrate annotation. *Nucleic Acids Research* 51(W1), W115-W121.
- Whokaryote: Pronk, L.J.U. & Medema, M.H. (2022). Whokaryote: distinguishing eukaryotic and prokaryotic contigs in metagenomes based on gene structure. *Microbial Genomics* 8(5), 000823.
- Tiara: Karlicki, M., Antonowicz, S. & Karnkowska, A. (2022). Tiara: deep learning-based classification system for eukaryotic sequences. *Bioinformatics* 38(2), 344-350.
- Bowtie2: Langmead, B. & Salzberg, S.L. (2012) *Nature Methods* 9(4), 357-359.
- IQ-TREE: Wong, T.K.F. et al. (2025). IQ-TREE 3: phylogenomic inference software using complex evolutionary models. *bioRxiv*. + UFBoot2: Hoang, D.T. et al. (2018) *Molecular Biology and Evolution* 35(2), 518-522.
- Shi, M. et al. (2016). Redefining the invertebrate RNA virosphere. *Nature* 540, 539-543. (RdRp-domain-directed viral discovery precedent, Camada 3)

Biological background citations:
- Backus, E.A., Serrano, M.S. & Ranger, C.M. (2005). Mechanisms of hopperburn: an overview of insect taxonomy, behavior, and physiology. *Annual Review of Entomology* 50, 125-151.
- Hernandez, C.A. et al. (2022). Spittlebugs (Hemiptera: Cercopidae): integrated pest management on gramineous crops in the Neotropical ecozone. *Frontiers in Sustainable Food Systems* 6, 891417.
- McCutcheon, J.P. & Moran, N.A. (2007). Parallel genomic evolution and metabolic interdependence in an ancient symbiosis. *PNAS* 104(49), 19392-19397.
- Bennett, G.M. & Moran, N.A. (2013). Small, smaller, smallest: the origins and evolution of ancient dual symbioses in a phloem-feeding insect. *Genome Biology and Evolution* 5(9), 1675-1688.
- Koga, R. & Moran, N.A. (2014). Swapping symbionts in spittlebugs: evolutionary replacement of a reduced genome symbiont. *The ISME Journal* 8, 1237-1249.
- Foieri, F., Decker-Franco, C., Marino de Remes Lenicov, A.M. & Arneodo, J.D. (2022). First identification of bacterial endosymbionts in three South-American spittlebug pests: *Notozulia entreriana*, *Deois mourei* and *Deois knoblauchii*. *Bulletin of Insectology*.
- Monteiro, L.P. (2019). Caracterizacao molecular da interacao das cigarrinhas-das-pastagens (*Mahanarva spectabilis*) com diferentes forrageiras. MSc dissertation, UFV.
- Rinaldi, A.J. (2021). Analise de componentes moleculares da espuma e da toxina presente na glandula salivar de cigarrinha das pastagens. MSc dissertation, UFV.
- Rinaldi, A.J. et al. (2026). Molecular and structural characterization of foam proteins from *Mahanarva spectabilis* nymphs reveals adaptive features and potential targets for pest control. *Archives of Insect Biochemistry and Physiology*.

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
