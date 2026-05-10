# Database Setup Guide / Guia de Configuracao dos Bancos de Dados

This document provides step-by-step instructions for downloading and building all reference databases required for the functional annotation pipeline of the *Mahanarva spectabilis* salivary gland transcriptome.

**Important:** These databases require substantial disk space and download time. Run these steps on the server or workstation where annotation will be performed. Databases do not need to be in the repository directory.

---

## Disk Space Requirements

| Database | Compressed Download | Uncompressed / Built Size | Notes |
|----------|--------------------|-----------------------------|-------|
| NCBI NR (FASTA) | ~100 GB | ~420 GB (DIAMOND .dmnd) | Required for DIAMOND BLASTx |
| eggNOG databases | ~30 GB | ~50 GB | 3 files required |
| NCBI taxdump | ~70 MB | ~70 MB | For taxonkit organism names |
| Pfam-A.hmm | ~250 MB | ~500 MB (after hmmpress) | Required for HMMER domain search |

Recommended: at least 600 GB free disk space on the database partition.

---

## 1. DIAMOND NR Database

DIAMOND is used for fast protein sequence similarity search against NCBI NR.

### Download NR protein FASTA from NCBI FTP

```bash
# Create a dedicated directory for databases
mkdir -p /path/to/databases/nr
cd /path/to/databases/nr

# Download the NR protein FASTA file (compressed, ~100 GB)
# This may take several hours depending on connection speed
wget -c "https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz" \
     -o wget_nr.log

# Verify download integrity
wget "https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz.md5"
md5sum -c nr.gz.md5
```

### Build DIAMOND database

```bash
# Decompress NR (requires ~250 GB temporary space during decompression)
# Alternatively, DIAMOND can read .gz directly:

diamond makedb \
    --in nr.gz \
    --db nr \
    --threads 16

# Output: nr.dmnd (~420 GB)
```

**Note about taxonomy in this project:**

This project builds the DIAMOND database **without** the `--taxonmap`, `--taxonnodes`, and `--taxonnames` flags. Organism names are extracted directly from the `stitle` (subject title) field of DIAMOND output using a regular expression that parses the bracketed organism name from NR FASTA headers (e.g., `[Acyrthosiphon pisum]`). This approach avoids the need to maintain synchronized taxonomy files alongside the NR database and works reliably for downstream species-of-origin assignment.

If taxonomy-aware filtering is needed in future analyses, rebuild with:

```bash
# Taxonomy-aware build (NOT used in this project)
diamond makedb \
    --in nr.gz \
    --db nr_taxon \
    --taxonmap prot.accession2taxid.FULL.gz \
    --taxonnodes taxdump/nodes.dmp \
    --taxonnames taxdump/names.dmp \
    --threads 16
```

---

## 2. NCBI Taxdump (for taxonkit)

taxonkit is used to resolve NCBI taxon IDs to organism names and lineages. It requires the NCBI taxonomy dump files.

```bash
mkdir -p /path/to/databases/taxdump
cd /path/to/databases/taxdump

# Download taxonomy dump (compressed, ~70 MB)
wget -c "https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz"

# Extract
tar -zxvf taxdump.tar.gz

# Extracted files include:
#   names.dmp    - taxon names (scientific, common, synonyms)
#   nodes.dmp    - taxonomy tree structure (parent, rank)
#   merged.dmp   - merged/deprecated taxon IDs
#   delnodes.dmp - deleted taxon IDs

# Set environment variable so taxonkit finds the database
export TAXONKIT_DB=/path/to/databases/taxdump

# Add to your shell profile for persistence:
echo 'export TAXONKIT_DB=/path/to/databases/taxdump' >> ~/.bashrc

# Verify taxonkit installation
taxonkit list --ids 6656 --indent ""  # Should list Arthropoda descendants
```

---

## 3. eggNOG Databases

eggNOG-mapper assigns GO terms, KEGG orthologs (KOs), and COG categories using the eggNOG v5 database.

### Important: Mirror status

As of 2024, the primary eggNOG database server at **eggnogdb.embl.de is offline**. Use the alternative download location at **eggnog5.embl.de** instead.

The `download_eggnog_data.py` script (bundled with eggnog-mapper) may fail if it tries the offline mirror. In that case, download the three required files manually:

### Manual download from eggnog5.embl.de

```bash
mkdir -p /path/to/databases/eggnog
cd /path/to/databases/eggnog

# File 1: eggNOG HMM database (main annotation database, ~25 GB compressed)
wget -c "http://eggnog5.embl.de/download/eggnog_5.0/eggnog.db.gz"

# File 2: eggNOG taxonomy database (~2 GB compressed)
wget -c "http://eggnog5.embl.de/download/eggnog_5.0/eggnog.taxa.tar.gz"

# File 3: eggNOG diamond database for fast seed ortholog search (~3 GB compressed)
wget -c "http://eggnog5.embl.de/download/eggnog_5.0/eggnog_proteins.dmnd.gz"

# Decompress
gunzip eggnog.db.gz
tar -zxvf eggnog.taxa.tar.gz
gunzip eggnog_proteins.dmnd.gz

# Verify file sizes (approximate)
ls -lh eggnog.db             # ~50 GB
ls -lh eggnog_proteins.dmnd  # ~8 GB
```

### Alternative: use download_eggnog_data.py with explicit data dir

If the download script is working:

```bash
# Activate annotation conda environment first
conda activate annotation

download_eggnog_data.py \
    --data_dir /path/to/databases/eggnog \
    -y
```

### Configure eggNOG-mapper data directory

```bash
# Set data directory when running emapper.py:
emapper.py \
    --data_dir /path/to/databases/eggnog \
    [... other options ...]

# Or set environment variable:
export EGGNOG_DATA_DIR=/path/to/databases/eggnog
```

---

## 4. Pfam-A HMM Database

HMMER searches the Pfam-A database to identify conserved protein domains.

```bash
mkdir -p /path/to/databases/pfam
cd /path/to/databases/pfam

# Download Pfam-A HMM library from EBI (compressed, ~250 MB)
wget -c "https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz"

# Decompress
gunzip Pfam-A.hmm.gz

# Build HMMER binary indexes for fast searching
# hmmpress creates 4 binary index files (.h3i, .h3m, .h3p, .h3f)
hmmpress Pfam-A.hmm

# Verify index files created
ls -lh Pfam-A.hmm*
# Expected output:
#   Pfam-A.hmm       (~500 MB)
#   Pfam-A.hmm.h3i   (index)
#   Pfam-A.hmm.h3m   (model)
#   Pfam-A.hmm.h3p   (profile)
#   Pfam-A.hmm.h3f   (filter)
```

---

## 5. Update Database Paths in Annotation Scripts

After downloading and building all databases, update the path variables at the top of these scripts:

- `03_annotation/04_diamond_nr.sh` - set `DIAMOND_DB` to the full path of `nr.dmnd`
- `03_annotation/05_eggnog_pfam.sh` - set `EGGNOG_DATA_DIR` and `PFAM_HMM` paths

Example:

```bash
# In 04_diamond_nr.sh:
DIAMOND_DB="/path/to/databases/nr/nr.dmnd"

# In 05_eggnog_pfam.sh:
EGGNOG_DATA_DIR="/path/to/databases/eggnog"
PFAM_HMM="/path/to/databases/pfam/Pfam-A.hmm"
```

---

## 6. Verification Checklist

Before running annotation, verify all databases are present and valid:

```bash
# DIAMOND NR
test -f /path/to/databases/nr/nr.dmnd && echo "PASS: nr.dmnd found" || echo "FAIL: nr.dmnd missing"

# taxdump
test -f /path/to/databases/taxdump/names.dmp && echo "PASS: taxdump found" || echo "FAIL: taxdump missing"
test -f /path/to/databases/taxdump/nodes.dmp && echo "PASS: nodes.dmp found" || echo "FAIL: nodes.dmp missing"

# eggNOG
test -f /path/to/databases/eggnog/eggnog.db && echo "PASS: eggnog.db found" || echo "FAIL: eggnog.db missing"
test -f /path/to/databases/eggnog/eggnog_proteins.dmnd && echo "PASS: eggnog_proteins.dmnd found" || echo "FAIL: eggnog_proteins.dmnd missing"

# Pfam
test -f /path/to/databases/pfam/Pfam-A.hmm && echo "PASS: Pfam-A.hmm found" || echo "FAIL: Pfam-A.hmm missing"
test -f /path/to/databases/pfam/Pfam-A.hmm.h3i && echo "PASS: hmmpress indexes found" || echo "FAIL: run hmmpress Pfam-A.hmm"
```

---

## Notes

- Database versions should be recorded in any publication using this pipeline. Run `diamond --version`, `hmmer --version`, and check the dates on downloaded files.
- NCBI NR is updated continuously. For reproducibility, note the download date.
- eggNOG version 5.0 is used throughout this project.
- Pfam release version is listed in the header of `Pfam-A.hmm` (check with `head -5 Pfam-A.hmm`).
