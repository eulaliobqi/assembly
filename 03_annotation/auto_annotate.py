#!/usr/bin/env python3
"""
AutoAnnotate - functional annotation pipeline for Trinity+TransDecoder proteins.

Phases:
  1. validate   - check prerequisites (mamba/conda, disk, RAM, connectivity)
  2. install    - deploy tools via conda/mamba
  3. databases  - validate pre-installed databases
  4. annotate   - DIAMOND -> TaxonKit -> eggNOG-mapper -> HMMER/Pfam
  5. integrate  - merge all results into annotation_complete.tsv
  6. report     - statistics summary

Usage:
  python auto_annotate.py --input gland-saliv-cigarr.fa [--outdir results] [--threads 8]
  python auto_annotate.py --input gland-saliv-cigarr.fa --resume
  python auto_annotate.py --input gland-saliv-cigarr.fa --phase annotate
"""

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# --- constants ----------------------------------------------------------------

REQUIRED_DISK_GB = 50
REQUIRED_RAM_GB  = 16
MAX_RETRIES      = 3
RETRY_BACKOFF    = [30, 90, 270]

CONDA_TOOLS = {
    "diamond":       ("bioconda", "diamond"),
    "taxonkit":      ("bioconda", "taxonkit"),
    "eggnog-mapper": ("bioconda", "eggnog-mapper"),
    "hmmer":         ("bioconda", "hmmer"),
}

# --- paths of pre-installed databases ----------------------------------------
DB_NR_DMND  = "/home/eulalio/databases/nr/nr.dmnd"
DB_TAXDUMP  = "/home/eulalio/databases/taxdump"
DB_EGGNOG   = "/home/eulalio/databases/eggnog"
DB_PFAM_HMM = "/home/eulalio/databases/pfam/Pfam-A.hmm"

STATE_FILE = "agent_state.json"
PHASES = ["validate", "install", "databases", "annotate", "integrate", "report"]

# --- logging ------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("auto_annotate.log"),
    ],
)
log = logging.getLogger("auto_annotate")

# add conda env bin to PATH so emapper.py and hmmscan are found
_CONDA_BIN = "/home/eulalio/miniforge3/envs/auto_annotate/bin"
if _CONDA_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _CONDA_BIN + ":" + os.environ.get("PATH", "")


# --- state persistence --------------------------------------------------------

def load_state(outdir):
    p = outdir / STATE_FILE
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {"completed_phases": [], "db_paths": {}}


def save_state(state, outdir):
    p = outdir / STATE_FILE
    with open(p, "w") as f:
        json.dump(state, f, indent=2)


# --- helpers ------------------------------------------------------------------

def run(cmd, check=True, capture=False, retries=0):
    cmd_str = " ".join(str(c) for c in cmd)
    for attempt in range(retries + 1):
        log.info("$ %s", cmd_str)
        result = subprocess.run(cmd, capture_output=capture, text=True)
        if result.returncode == 0 or not check:
            return result
        if attempt < retries:
            wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
            log.warning("Command failed (attempt %d/%d), retrying in %ds...",
                        attempt + 1, retries + 1, wait)
            time.sleep(wait)
        else:
            log.error("Command failed: %s\nstderr: %s", cmd_str, result.stderr or "")
            if check:
                raise RuntimeError("Command failed: " + cmd_str)
    return result


def which_tool(name):
    return shutil.which(name)


def mamba_or_conda():
    return "mamba" if which_tool("mamba") else "conda"


# --- phase 1: validate --------------------------------------------------------

def phase_validate(args, state):
    log.info("=== Phase 1: Validate prerequisites ===")
    errors = []

    if not Path(args.input).exists():
        errors.append("Input file not found: " + args.input)

    mgr = mamba_or_conda()
    if not which_tool(mgr):
        errors.append("conda/mamba not found")
    else:
        log.info("Package manager: %s", mgr)

    stat = shutil.disk_usage(args.outdir)
    free_gb = stat.free / 1e9
    if free_gb < REQUIRED_DISK_GB:
        log.warning("Free disk: %.1f GB (recommended: %d GB)", free_gb, REQUIRED_DISK_GB)
    else:
        log.info("Disk: %.1f GB free", free_gb)

    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / 1e9
        if ram_gb < REQUIRED_RAM_GB:
            log.warning("RAM: %.1f GB (recommended: %d GB)", ram_gb, REQUIRED_RAM_GB)
        else:
            log.info("RAM: %.1f GB", ram_gb)
    except ImportError:
        log.info("psutil not installed - skipping RAM check")

    try:
        import urllib.request
        urllib.request.urlopen("https://ftp.ncbi.nlm.nih.gov", timeout=10)
        log.info("Network: NCBI FTP reachable")
    except Exception as e:
        log.warning("Network check failed: %s", e)

    if errors:
        for e in errors:
            log.error("FATAL: %s", e)
        sys.exit(1)

    log.info("Validation passed.")
    return state


# --- phase 2: install tools ---------------------------------------------------

def phase_install(args, state):
    log.info("=== Phase 2: Install tools ===")
    mgr = mamba_or_conda()

    for tool, (channel, pkg) in CONDA_TOOLS.items():
        if which_tool(tool):
            log.info("  %-20s already in PATH, skipping", tool)
            continue
        log.info("  Installing %s from %s...", pkg, channel)
        run([mgr, "install", "-y", "-c", channel, "-c", "conda-forge", pkg], retries=2)

    missing = [t for t in CONDA_TOOLS if not which_tool(t)]
    if missing:
        log.warning("Still not in PATH after install: %s", missing)
        log.warning("If running inside conda env, activate it first.")

    log.info("Tool installation complete.")
    return state


# --- phase 3: databases -------------------------------------------------------

def phase_databases(args, state):
    log.info("=== Phase 3: Validate pre-installed databases ===")

    checks = {
        "NR DIAMOND":  DB_NR_DMND,
        "taxdump":     str(Path(DB_TAXDUMP) / "names.dmp"),
        "eggNOG DB":   str(Path(DB_EGGNOG)  / "eggnog.db"),
        "eggNOG DMND": str(Path(DB_EGGNOG)  / "eggnog_proteins.dmnd"),
        "Pfam HMM":    DB_PFAM_HMM,
    }

    missing = []
    for name, path in checks.items():
        if Path(path).exists():
            log.info("  %-15s OK  (%s)", name, path)
        else:
            log.error("  %-15s MISSING  (%s)", name, path)
            missing.append(name)

    if missing:
        log.error("Missing databases: %s", missing)
        sys.exit(1)

    state["db_paths"] = {
        "nr_dmnd":    DB_NR_DMND,
        "taxdump":    DB_TAXDUMP,
        "eggnog_dir": DB_EGGNOG,
        "pfam_hmm":   DB_PFAM_HMM,
    }
    os.environ["TAXONKIT_DB"] = DB_TAXDUMP
    save_state(state, Path(args.outdir))
    log.info("All databases verified.")
    return state


# --- phase 4: annotate --------------------------------------------------------

def phase_annotate(args, state):
    log.info("=== Phase 4: Annotate ===")
    out     = Path(args.outdir)
    inp     = Path(args.input)
    db      = state["db_paths"]
    threads = str(args.threads)

    # Step 4a: DIAMOND BLASTp vs NR
    diamond_out = out / "diamond_nr.tsv"
    if not diamond_out.exists():
        log.info("Running DIAMOND BLASTp vs NR...")
        run([
            "diamond", "blastp",
            "--db",    db["nr_dmnd"],
            "--query", str(inp),
            "--out",   str(diamond_out),
            "--outfmt", "6",
            "qseqid", "sseqid", "pident", "length", "mismatch", "gapopen",
            "qstart", "qend", "sstart", "send", "evalue", "bitscore",
            "stitle",
            "--evalue",          "1e-5",
            "--max-target-seqs", "1",
            "--id",              "30",
            "--query-cover",     "50",
            "--threads",         threads,
            "--sensitive",
        ])
        log.info("DIAMOND complete: %s", diamond_out)
    else:
        log.info("DIAMOND output already present, skipping.")

    # Step 4b: TaxonKit lineage classification via name2taxid
    taxon_out = out / "taxon_lineage.tsv"
    if not diamond_out.exists():
        log.warning("DIAMOND output missing - cannot run TaxonKit.")
    elif not taxon_out.exists():
        log.info("Classifying organisms with TaxonKit...")

        names_file = out / "organism_names.txt"
        with open(diamond_out) as fin, open(names_file, "w") as fout:
            seen = set()
            for line in fin:
                parts = line.split("\t")
                if len(parts) >= 13:
                    title = parts[12].strip()
                    m = re.search(r'\[([^\[\]]+)\]', title)
                    if m:
                        name = m.group(1)
                        if name not in seen:
                            seen.add(name)
                            fout.write(name + "\n")

        env = os.environ.copy()
        env["TAXONKIT_DB"] = db["taxdump"]

        proc = subprocess.run(
            ["taxonkit", "name2taxid", "--data-dir", db["taxdump"], str(names_file)],
            capture_output=True, text=True, env=env,
        )
        name2tid_file = out / "name2taxid.tsv"
        with open(name2tid_file, "w") as f:
            f.write(proc.stdout)

        taxids = []
        for line in proc.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1].strip():
                taxids.append(parts[1].strip())

        if taxids:
            taxids_file = out / "taxids.txt"
            with open(taxids_file, "w") as f:
                f.write("\n".join(set(taxids)) + "\n")

            proc2 = subprocess.run(
                ["taxonkit", "lineage", "--data-dir", db["taxdump"], str(taxids_file)],
                capture_output=True, text=True, env=env,
            )
            with open(out / "lineage_raw.tsv", "w") as f:
                f.write(proc2.stdout)

            proc3 = subprocess.run(
                ["taxonkit", "reformat", "--data-dir", db["taxdump"],
                 "--format", "{k};{p};{c};{o};{f};{g};{s}",
                 str(out / "lineage_raw.tsv")],
                capture_output=True, text=True, env=env,
            )
            with open(taxon_out, "w") as f:
                f.write(proc3.stdout)

        log.info("TaxonKit complete: %s", taxon_out)
    else:
        log.info("Taxon lineage already present, skipping.")

    # Step 4c: eggNOG-mapper (GO + KEGG)
    emapper_prefix = str(out / "emapper")
    emapper_out    = out / "emapper.emapper.annotations"
    if not emapper_out.exists():
        log.info("Running eggNOG-mapper...")
        run([
            "emapper.py",
            "-i",         str(inp),
            "--itype",    "proteins",
            "-o",         emapper_prefix,
            "--data_dir", db["eggnog_dir"],
            "--cpu",      threads,
            "--override",
        ], retries=1)
        log.info("eggNOG-mapper complete: %s", emapper_out)
    else:
        log.info("eggNOG-mapper output already present, skipping.")

    # Step 4d: HMMER vs Pfam
    hmmer_out = out / "pfam_hits.tbl"
    if not hmmer_out.exists():
        log.info("Running HMMER hmmscan vs Pfam-A...")
        run([
            "hmmscan",
            "--cpu",       threads,
            "--tblout",    str(hmmer_out),
            "--domtblout", str(out / "pfam_domhits.tbl"),
            "-E",          "1e-5",
            "--domE",      "1e-5",
            db["pfam_hmm"],
            str(inp),
        ])
        log.info("HMMER complete: %s", hmmer_out)
    else:
        log.info("HMMER output already present, skipping.")

    log.info("Annotation phase complete.")
    return state


# --- phase 5: integrate -------------------------------------------------------

def _extract_organism(title):
    m = re.search(r'\[([^\[\]]+)\]', title)
    return m.group(1) if m else ""


def _parse_diamond(path):
    hits = {}
    if not path.exists():
        return hits
    with open(path) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 13:
                continue
            qid = parts[0]
            if qid not in hits:
                title   = parts[12].strip()
                sciname = _extract_organism(title)
                hits[qid] = {
                    "diamond_subject":  parts[1],
                    "diamond_pident":   parts[2],
                    "diamond_evalue":   parts[10],
                    "diamond_bitscore": parts[11],
                    "diamond_sciname":  sciname,
                    "diamond_title":    title,
                }
    return hits


def _parse_taxon(path):
    """Keyed by taxid; uses full lineage (col 1) which contains 'Eukaryota'."""
    lin = {}
    if not path.exists():
        return lin
    with open(path) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                lin[parts[0].strip()] = parts[1].strip()
    return lin


def _build_name2taxid(outdir):
    n2t = {}
    p = outdir / "name2taxid.tsv"
    if not p.exists():
        return n2t
    with open(p) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2 and parts[1].strip():
                n2t[parts[0].strip()] = parts[1].strip()
    return n2t


def _classify_taxonomy(lineage):
    l = lineage.lower()
    return {
        "is_eukaryote": int("eukaryota" in l),
        "is_bacteria":  int("bacteria"  in l),
        "is_fungi":     int("fungi"     in l),
        "is_virus":     int("viruses"   in l or "viridae" in l),
    }


def _parse_emapper(path):
    # emapper 2.1.12 columns (0-indexed): 0 query, 1 seed_ortholog, 2 evalue,
    # 3 score, 4 eggNOG_OGs, 5 max_annot_lvl, 6 COG_category, 7 Description,
    # 8 Preferred_name, 9 GOs, 10 EC, 11 KEGG_ko, 12 KEGG_Pathway, ...,
    # 18 CAZy. eggnog_og previously read parts[1] (seed_ortholog) instead of
    # parts[4] (eggNOG_OGs) -- fixed here.
    em = {}
    if not path.exists():
        return em
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 10:
                continue
            qid = parts[0]
            em[qid] = {
                "eggnog_gene_name": parts[8].strip()  if len(parts) > 8  else "",
                "go_terms":         parts[9].strip()  if len(parts) > 9  else "",
                "kegg_ko":          parts[11].strip() if len(parts) > 11 else "",
                "kegg_pathway":     parts[12].strip() if len(parts) > 12 else "",
                "eggnog_og":        parts[4].strip()  if len(parts) > 4  else "",
                "cog_category":     parts[6].strip()  if len(parts) > 6  else "",
                "eggnog_desc":      parts[7].strip()  if len(parts) > 7  else "",
                "cazy":             parts[18].strip() if len(parts) > 18 else "",
            }
    return em


def _parse_hmmer(path):
    pfam = {}
    if not path.exists():
        return pfam
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            if len(parts) < 19:
                continue
            domain = parts[0]
            acc    = parts[1]
            qid    = parts[2]
            evalue = parts[4]
            if qid not in pfam:
                pfam[qid] = {"pfam_domains": domain + "(" + acc + ")", "pfam_evalue": evalue}
            else:
                pfam[qid]["pfam_domains"] += ";" + domain + "(" + acc + ")"
    return pfam


def _parse_fasta_ids(path):
    ids = []
    with open(path) as f:
        for line in f:
            if line.startswith(">"):
                ids.append(line[1:].split()[0].strip())
    return ids


def phase_integrate(args, state):
    log.info("=== Phase 5: Integrate results ===")
    out = Path(args.outdir)

    proteins   = _parse_fasta_ids(Path(args.input))
    diamond    = _parse_diamond(out / "diamond_nr.tsv")
    taxon_lin  = _parse_taxon(out / "taxon_lineage.tsv")
    name2taxid = _build_name2taxid(out)
    emapper    = _parse_emapper(out / "emapper.emapper.annotations")
    pfam       = _parse_hmmer(out / "pfam_hits.tbl")

    header = [
        "protein_id", "gene_name",
        "diamond_subject", "diamond_pident", "diamond_evalue", "diamond_bitscore",
        "diamond_taxid", "diamond_sciname", "source_organism", "lineage",
        "is_eukaryote", "is_bacteria", "is_fungi", "is_virus",
        "go_terms", "kegg_ko", "kegg_pathway",
        "pfam_domains", "pfam_evalue",
        "eggnog_og", "cog_category", "eggnog_desc", "cazy", "diamond_title",
    ]

    tsv_out = out / "annotation_complete.tsv"
    with open(tsv_out, "w") as f:
        f.write("\t".join(header) + "\n")
        for pid in proteins:
            d       = diamond.get(pid, {})
            em      = emapper.get(pid, {})
            pf      = pfam.get(pid, {})
            sciname = d.get("diamond_sciname", "")
            taxid   = name2taxid.get(sciname, "")
            lineage = taxon_lin.get(taxid, "")
            flags   = _classify_taxonomy(lineage)
            gene    = em.get("eggnog_gene_name", "") or d.get("diamond_title", "")[:50]

            row = [
                pid, gene,
                d.get("diamond_subject",  ""),
                d.get("diamond_pident",   ""),
                d.get("diamond_evalue",   ""),
                d.get("diamond_bitscore", ""),
                taxid, sciname, sciname, lineage,
                str(flags["is_eukaryote"]),
                str(flags["is_bacteria"]),
                str(flags["is_fungi"]),
                str(flags["is_virus"]),
                em.get("go_terms",     ""),
                em.get("kegg_ko",      ""),
                em.get("kegg_pathway", ""),
                pf.get("pfam_domains", ""),
                pf.get("pfam_evalue",  ""),
                em.get("eggnog_og",    ""),
                em.get("cog_category", ""),
                em.get("eggnog_desc",  ""),
                em.get("cazy",         ""),
                d.get("diamond_title", ""),
            ]
            f.write("\t".join(row) + "\n")

    log.info("Integrated annotation: %s  (%d proteins)", tsv_out, len(proteins))
    state["output_tsv"] = str(tsv_out)
    save_state(state, out)
    return state


# --- phase 6: report ----------------------------------------------------------

def phase_report(args, state):
    log.info("=== Phase 6: Report ===")
    tsv_path = Path(state.get("output_tsv", Path(args.outdir) / "annotation_complete.tsv"))
    if not tsv_path.exists():
        log.warning("annotation_complete.tsv not found - run integrate phase first.")
        return state

    total = annotated = has_go = has_kegg = has_pfam = 0
    tax = {"eukaryote": 0, "bacteria": 0, "fungi": 0, "virus": 0, "unclassified": 0}

    with open(tsv_path) as f:
        header = f.readline().rstrip("\n").split("\t")
        idx = {h: i for i, h in enumerate(header)}
        for line in f:
            parts = line.rstrip("\n").split("\t")
            total += 1
            if parts[idx.get("diamond_subject", 2)]:
                annotated += 1
            if parts[idx.get("go_terms",      14)]:
                has_go   += 1
            if parts[idx.get("kegg_ko",       15)]:
                has_kegg += 1
            if parts[idx.get("pfam_domains",  17)]:
                has_pfam += 1
            is_e = parts[idx.get("is_eukaryote", 10)] == "1"
            is_b = parts[idx.get("is_bacteria",  11)] == "1"
            is_f = parts[idx.get("is_fungi",     12)] == "1"
            is_v = parts[idx.get("is_virus",     13)] == "1"
            if   is_f: tax["fungi"]        += 1
            elif is_e: tax["eukaryote"]    += 1
            elif is_b: tax["bacteria"]     += 1
            elif is_v: tax["virus"]        += 1
            else:      tax["unclassified"] += 1

    pct = lambda n: ("%.1f%%" % (100.0 * n / total)) if total else "N/A"

    lines = [
        "=" * 56,
        "  AutoAnnotate - Summary Report",
        "=" * 56,
        "  Input proteins      : %d"    % total,
        "  DIAMOND hits        : %d (%s)" % (annotated, pct(annotated)),
        "  With GO terms       : %d (%s)" % (has_go,    pct(has_go)),
        "  With KEGG KO        : %d (%s)" % (has_kegg,  pct(has_kegg)),
        "  With Pfam domain    : %d (%s)" % (has_pfam,  pct(has_pfam)),
        "",
        "  Taxonomic classification of best hits:",
        "    Eukaryota         : %d" % tax["eukaryote"],
        "    Bacteria          : %d" % tax["bacteria"],
        "    Fungi             : %d" % tax["fungi"],
        "    Viruses           : %d" % tax["virus"],
        "    Unclassified      : %d" % tax["unclassified"],
        "=" * 56,
    ]

    report_str = "\n".join(lines)
    print(report_str)

    report_path = Path(args.outdir) / "annotation_report.txt"
    with open(report_path, "w") as f:
        f.write(report_str + "\n")
    log.info("Report saved: %s", report_path)
    return state


# --- main ---------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="AutoAnnotate - functional annotation pipeline for Trinity+TransDecoder proteins",
    )
    p.add_argument("--input",   required=True, help="Input FASTA (protein sequences)")
    p.add_argument("--outdir",  default="results", help="Output directory (default: results)")
    p.add_argument("--threads", type=int, default=min(8, os.cpu_count() or 4))
    p.add_argument("--resume",  action="store_true", help="Resume from last completed phase")
    p.add_argument("--phase",   choices=PHASES, help="Run only a specific phase")
    return p.parse_args()


def main():
    args = parse_args()
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    state = load_state(Path(args.outdir))

    phase_funcs = {
        "validate":  phase_validate,
        "install":   phase_install,
        "databases": phase_databases,
        "annotate":  phase_annotate,
        "integrate": phase_integrate,
        "report":    phase_report,
    }

    if args.phase:
        phases_to_run = [args.phase]
    elif args.resume:
        done = set(state.get("completed_phases", []))
        phases_to_run = [ph for ph in PHASES if ph not in done]
        if not phases_to_run:
            log.info("All phases already completed.")
            return
    else:
        phases_to_run = PHASES

    for ph in phases_to_run:
        try:
            state = phase_funcs[ph](args, state)
            if ph not in state.get("completed_phases", []):
                state.setdefault("completed_phases", []).append(ph)
            save_state(state, Path(args.outdir))
        except Exception as e:
            log.error("Phase '%s' failed: %s", ph, e)
            save_state(state, Path(args.outdir))
            sys.exit(1)

    log.info("Pipeline complete. Results in: %s", args.outdir)


if __name__ == "__main__":
    main()
