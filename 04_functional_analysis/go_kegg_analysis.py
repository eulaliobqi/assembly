#!/usr/bin/env python3
"""
go_kegg_analysis.py - GO distribution and KEGG pathway analysis
for non-model hemipteran (Hemiptera) salivary gland proteins.

Reads directly from emapper.emapper.annotations (raw eggNOG output).

Usage:
  python go_kegg_analysis.py
  python go_kegg_analysis.py --emapper results/emapper.emapper.annotations
  python go_kegg_analysis.py --min-depth 4 --top-go 20 --top-kegg 30

Outputs:
  go_distribution.png/.tiff      - 3-panel GO bar chart (BP, MF, CC)
  kegg_pathways_bar.png/.tiff    - horizontal bar chart, top 20 KEGG pathways
  kegg_pathways_bubble.png/.tiff - bubble chart, top 30 KEGG pathways
  go_top20_BP/MF/CC.csv          - GO frequency tables
  kegg_pathways.csv              - KEGG pathway frequency table
"""

import argparse
import json
import os
import sys
import time
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import requests

# --- configuration ------------------------------------------------------------

DEFAULT_EMAPPER = "results/emapper.emapper.annotations"
DEFAULT_ANNOT   = "results/annotation_complete.tsv"
OBO_PATH        = "go-basic.obo"
OBO_URL         = "http://purl.obolibrary.org/obo/go/go-basic.obo"
KEGG_BASE       = "https://rest.kegg.jp"
TOTAL_PROTEINS  = 12445   # fallback if annotation_complete.tsv not found

NAMESPACE_SHORT = {
    "biological_process": "BP",
    "molecular_function": "MF",
    "cellular_component": "CC",
}

NS_LABELS = {
    "BP": "Biological Process",
    "MF": "Molecular Function",
    "CC": "Cellular Component",
}

NS_COLORS = {
    "BP": "#2C7BB6",
    "MF": "#F07D0C",
    "CC": "#1A9641",
}

KEGG_CAT_COLORS = {
    "Metabolism":                           "#D7191C",
    "Genetic Information Processing":       "#2C7BB6",
    "Environmental Information Processing": "#1A9641",
    "Cellular Processes":                   "#F07D0C",
    "Organismal Systems":                   "#7B2D8B",
    "Human Diseases":                       "#8B7355",
    "Drug Development":                     "#808080",
    "Other":                                "#BDBDBD",
}

plt.rcParams.update({
    "font.family":       "Arial",
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "axes.linewidth":    0.8,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

# --- data loading -------------------------------------------------------------

def get_total_proteins(annot_path):
    if not os.path.exists(annot_path):
        print("[WARN] annotation_complete.tsv not found, using default total=%d" % TOTAL_PROTEINS)
        return TOTAL_PROTEINS
    with open(annot_path) as f:
        return sum(1 for line in f) - 1


def parse_emapper(path):
    """
    Parse emapper.emapper.annotations.
    Returns dict: {protein_id: {go_terms, kegg_ko, kegg_pathway, cog_category, description}}

    Column layout (emapper v2.1.x):
      0  query          6  COG_category   9  GOs
      1  seed_ortholog  7  Description   11  KEGG_ko
      4  eggNOG_OGs     8  Preferred_name 12  KEGG_Pathway
    """
    data = {}
    if not os.path.exists(path):
        sys.exit("[ERROR] emapper file not found: %s" % path)

    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 10:
                continue

            pid = parts[0]

            # GO terms: comma-separated GO:XXXXXXX, may be '-'
            go_raw = parts[9].strip() if len(parts) > 9 else ""
            go_terms = []
            if go_raw and go_raw != "-":
                for g in go_raw.split(","):
                    g = g.strip()
                    if g.startswith("GO:"):
                        go_terms.append(g)

            # KEGG KO: comma-separated ko:KXXXXX, may be '-'
            ko_raw = parts[11].strip() if len(parts) > 11 else ""
            kegg_ko = []
            if ko_raw and ko_raw != "-":
                for k in ko_raw.split(","):
                    k = k.strip().replace("ko:", "")
                    if k:
                        kegg_ko.append(k)

            # KEGG Pathway: comma-separated, keep only 'map' prefix
            pw_raw = parts[12].strip() if len(parts) > 12 else ""
            kegg_pathway = []
            if pw_raw and pw_raw != "-":
                for p in pw_raw.split(","):
                    p = p.strip()
                    if p.startswith("map"):
                        kegg_pathway.append(p)

            data[pid] = {
                "go_terms":     go_terms,
                "kegg_ko":      kegg_ko,
                "kegg_pathway": kegg_pathway,
                "cog_category": parts[6].strip() if len(parts) > 6 else "",
                "description":  parts[7].strip() if len(parts) > 7 else "",
            }

    n_go   = sum(1 for d in data.values() if d["go_terms"])
    n_kegg = sum(1 for d in data.values() if d["kegg_pathway"])
    print("[emapper] %d proteins parsed | %d with GO | %d with KEGG pathway" %
          (len(data), n_go, n_kegg))
    return data


# --- GO analysis --------------------------------------------------------------

def download_obo(path=OBO_PATH, url=OBO_URL):
    if os.path.exists(path):
        print("[OBO] Using cached %s" % path)
        return
    print("[OBO] Downloading go-basic.obo ...")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; bioinformatics-pipeline/1.0)"}
    resp = requests.get(url, headers=headers, stream=True, timeout=60)
    resp.raise_for_status()
    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)
    print("[OBO] Saved to %s (%.1f MB)" % (path, os.path.getsize(path) / 1e6))


def parse_obo(path=OBO_PATH):
    """
    Minimal OBO parser - no external dependency.
    Returns dict: {go_id: {name, namespace, depth(approx), is_obsolete}}
    depth is approximated by counting 'is_a' ancestors (BFS not required for top-N).
    """
    print("[OBO] Parsing %s ..." % path)
    terms = {}
    parents = {}   # go_id -> [parent_go_ids]

    current = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "[Term]":
                current = {}
            elif line == "" and current is not None:
                tid = current.get("id")
                if tid:
                    terms[tid] = current
                current = None
            elif current is not None:
                if line.startswith("id: "):
                    current["id"] = line[4:].strip()
                elif line.startswith("name: "):
                    current["name"] = line[6:].strip()
                elif line.startswith("namespace: "):
                    current["namespace"] = line[11:].strip()
                elif line.startswith("is_obsolete: true"):
                    current["is_obsolete"] = True
                elif line.startswith("is_a: "):
                    parent_id = line[6:].split("!")[0].strip()
                    current.setdefault("parents", []).append(parent_id)

    # compute approximate depth via BFS
    depths = {}
    roots  = {"GO:0008150", "GO:0003674", "GO:0005575"}  # BP, MF, CC roots
    for r in roots:
        depths[r] = 0

    changed = True
    max_iter = 20
    while changed and max_iter > 0:
        changed   = False
        max_iter -= 1
        for tid, t in terms.items():
            if t.get("is_obsolete"):
                continue
            for par in t.get("parents", []):
                if par in depths:
                    new_depth = depths[par] + 1
                    if tid not in depths or depths[tid] < new_depth:
                        depths[tid] = new_depth
                        changed = True

    result = {}
    for tid, t in terms.items():
        if t.get("is_obsolete"):
            continue
        ns = NAMESPACE_SHORT.get(t.get("namespace", ""), None)
        if ns is None:
            continue
        result[tid] = {
            "name":      t.get("name", tid),
            "namespace": ns,
            "depth":     depths.get(tid, 1),
        }

    print("[OBO] Loaded %d GO terms" % len(result))
    return result


def build_go_frequency(emapper_data, godict, min_depth=3):
    """
    Count distinct proteins per GO term.
    Returns {ns: Counter({go_id: protein_count})}, {go_id: (name, depth, ns)}
    """
    counters = {"BP": Counter(), "MF": Counter(), "CC": Counter()}
    go_info  = {}

    for pid, data in emapper_data.items():
        seen = set()
        for go_id in data["go_terms"]:
            if go_id in seen:
                continue
            seen.add(go_id)
            term = godict.get(go_id)
            if term is None:
                continue
            if term["depth"] < min_depth:
                continue
            ns = term["namespace"]
            counters[ns][go_id] += 1
            go_info[go_id] = (term["name"], term["depth"], ns)

    for ns, c in counters.items():
        print("[GO] %s: %d unique terms" % (ns, len(c)))
    return counters, go_info


def top_n_dfs(counters, go_info, n=20):
    result = {}
    for ns, counter in counters.items():
        rows = [{"go_id": gid, "name": go_info[gid][0],
                 "depth": go_info[gid][1], "count": cnt}
                for gid, cnt in counter.most_common(n)]
        result[ns] = pd.DataFrame(rows)
    return result


def plot_go_distribution(top_dfs, out_base="go_distribution", total=TOTAL_PROTEINS, min_depth=3):
    fig, axes = plt.subplots(1, 3, figsize=(18, 8))

    for ax, ns in zip(axes, ["BP", "MF", "CC"]):
        df = top_dfs[ns].copy()
        if df.empty:
            ax.set_title(NS_LABELS[ns])
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center")
            continue

        labels = [n[:55] + "..." if len(n) > 55 else n for n in df["name"]]
        y = np.arange(len(labels))

        ax.barh(y, df["count"], height=0.65, color=NS_COLORS[ns], alpha=0.88, zorder=3)

        for i, cnt in enumerate(df["count"]):
            pct = 100.0 * cnt / total
            ax.text(cnt + max(df["count"]) * 0.015, i,
                    "%.1f%%" % pct, va="center", ha="left", fontsize=8.5)

        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8.5)
        ax.invert_yaxis()
        ax.set_xlabel("Number of proteins")
        ax.set_title(NS_LABELS[ns], fontweight="bold", pad=6)
        ax.grid(axis="x", color="#e0e0e0", lw=0.5, zorder=0)
        ax.tick_params(axis="y", length=0)
        ax.set_xlim(right=max(df["count"]) * 1.20)

    fig.suptitle(
        "GO Term Distribution - Salivary Gland Proteome\n"
        "(n = %s proteins, GO depth >= %d)" % (f"{total:,}", min_depth),
        fontsize=12, fontweight="bold", y=1.02
    )
    fig.tight_layout()

    fig.savefig(out_base + ".png",  dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(out_base + ".tiff", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("[GO] Saved: %s.png / .tiff" % out_base)


# --- KEGG analysis ------------------------------------------------------------

def _fetch(url, max_retries=5):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.text
            if resp.status_code == 403:
                wait = 4 ** (attempt + 1)
                print("[KEGG] 403 throttle, waiting %ds ..." % wait)
                time.sleep(wait)
            else:
                resp.raise_for_status()
        except Exception as e:
            wait = 3 ** (attempt + 1)
            print("[KEGG] Error: %s. Retry %d/%d in %ds ..." % (e, attempt + 1, max_retries, wait))
            time.sleep(wait)
    raise RuntimeError("Failed to fetch: %s" % url)


def fetch_pathway_names(cache="kegg_pathway_names.json"):
    if os.path.exists(cache):
        with open(cache) as f:
            d = json.load(f)
        print("[KEGG] Pathway names loaded from cache (%d entries)" % len(d))
        return d

    print("[KEGG] Fetching pathway names from KEGG REST API ...")
    text = _fetch(KEGG_BASE + "/list/pathway")
    time.sleep(1.2)

    names = {}
    for line in text.strip().split("\n"):
        if "\t" not in line:
            continue
        pid, name = line.split("\t", 1)
        pid = pid.replace("path:", "").strip()
        names[pid] = name.strip()

    with open(cache, "w") as f:
        json.dump(names, f, indent=2)
    print("[KEGG] %d pathway names saved to %s" % (len(names), cache))
    return names


def fetch_pathway_categories(cache="kegg_pathway_categories.json"):
    if os.path.exists(cache):
        with open(cache) as f:
            d = json.load(f)
        print("[KEGG] Pathway categories loaded from cache (%d entries)" % len(d))
        return d

    print("[KEGG] Fetching KEGG BRITE hierarchy (br:ko00001) ...")
    text = _fetch(KEGG_BASE + "/get/br:ko00001/json")
    time.sleep(1.2)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print("[KEGG] JSON parse error: %s. Using empty category dict." % e)
        return {}

    cats = {}
    for top_node in data.get("children", []):
        raw_name  = top_node.get("name", "")
        top_label = " ".join(raw_name.split()[1:]) if raw_name else "Other"
        for sub in top_node.get("children", []):
            for pw_node in sub.get("children", []):
                raw_pw = pw_node.get("name", "")
                parts  = raw_pw.split()
                if parts and parts[0].isdigit():
                    map_id = "map" + parts[0].zfill(5)
                    cats[map_id] = top_label

    with open(cache, "w") as f:
        json.dump(cats, f, indent=2)
    print("[KEGG] %d pathway categories saved to %s" % (len(cats), cache))
    return cats


def build_kegg_table(emapper_data, pw_names, pw_cats, total_proteins):
    pw_counter = Counter()
    for pid, data in emapper_data.items():
        seen = set()
        for pw_id in data["kegg_pathway"]:
            if pw_id not in seen:
                seen.add(pw_id)
                pw_counter[pw_id] += 1

    rows = []
    for pw_id, cnt in pw_counter.items():
        rows.append({
            "pathway_id":    pw_id,
            "name":          pw_names.get(pw_id, pw_id),
            "category":      pw_cats.get(pw_id, "Other"),
            "protein_count": cnt,
            "pct_total":     round(100.0 * cnt / total_proteins, 2),
        })

    df = pd.DataFrame(rows).sort_values("protein_count", ascending=False)
    df.to_csv("kegg_pathways.csv", index=False)
    print("[KEGG] %d pathways | table saved to kegg_pathways.csv" % len(df))
    return df


def plot_kegg_bar(df, top_n=20, total=TOTAL_PROTEINS, out_base="kegg_pathways_bar"):
    top_df = df.head(top_n).copy().sort_values("protein_count", ascending=True)
    labels = [n[:52] + "..." if len(n) > 52 else n for n in top_df["name"]]
    colors = [KEGG_CAT_COLORS.get(c, "#BDBDBD") for c in top_df["category"]]

    fig, ax = plt.subplots(figsize=(11, 7))
    y = np.arange(len(labels))
    bars = ax.barh(y, top_df["protein_count"], height=0.65,
                   color=colors, alpha=0.88, zorder=3)

    for bar, cnt in zip(bars, top_df["protein_count"]):
        pct = 100.0 * cnt / total
        ax.text(bar.get_width() + max(top_df["protein_count"]) * 0.015,
                bar.get_y() + bar.get_height() / 2,
                "%d (%.1f%%)" % (cnt, pct),
                va="center", ha="left", fontsize=8.5)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Number of proteins")
    ax.set_title("Top %d KEGG Pathways - Salivary Gland Proteome\n(n = %s proteins)"
                 % (top_n, f"{total:,}"), fontweight="bold", pad=6)
    ax.set_xlim(right=max(top_df["protein_count"]) * 1.22)
    ax.grid(axis="x", color="#e0e0e0", lw=0.5, zorder=0)
    ax.tick_params(axis="y", length=0)

    unique_cats = top_df["category"].unique()
    handles = [mpatches.Patch(color=KEGG_CAT_COLORS.get(c, "#BDBDBD"), label=c)
               for c in sorted(unique_cats)]
    ax.legend(handles=handles, loc="lower right", frameon=False,
              fontsize=9, title="KEGG Category", title_fontsize=10)

    fig.tight_layout()
    fig.savefig(out_base + ".png",  dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(out_base + ".tiff", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("[KEGG] Saved: %s.png / .tiff" % out_base)


def plot_kegg_bubble(df, top_n=30, total=TOTAL_PROTEINS, out_base="kegg_pathways_bubble"):
    top_df = df.head(top_n).copy()
    cats   = sorted(top_df["category"].unique())
    cat_x  = {c: i for i, c in enumerate(cats)}

    fig, ax = plt.subplots(figsize=(14, 8))
    np.random.seed(42)

    for _, row in top_df.iterrows():
        x      = cat_x[row["category"]] + np.random.uniform(-0.3, 0.3)
        color  = KEGG_CAT_COLORS.get(row["category"], "#BDBDBD")
        size   = max(row["protein_count"] * 1.2, 20)
        ax.scatter(x, row["protein_count"], s=size,
                   c=color, alpha=0.75, edgecolors="white", linewidths=0.6, zorder=3)
        label = row["name"][:42] + "..." if len(row["name"]) > 42 else row["name"]
        ax.annotate(label, (x, row["protein_count"]),
                    xytext=(5, 3), textcoords="offset points",
                    fontsize=7.5, ha="left", va="bottom")

    ax.set_xticks(list(cat_x.values()))
    ax.set_xticklabels(list(cat_x.keys()), rotation=28, ha="right", fontsize=9)
    ax.set_ylabel("Number of proteins")
    ax.set_title(
        "KEGG Pathway Distribution - Salivary Gland Proteome\n"
        "Top %d pathways (n = %s proteins total)" % (top_n, f"{total:,}"),
        fontweight="bold", pad=8
    )
    ax.grid(axis="y", color="#e0e0e0", lw=0.5, zorder=0)

    handles = [mpatches.Patch(color=KEGG_CAT_COLORS.get(c, "#BDBDBD"), label=c)
               for c in cats]
    ax.legend(handles=handles, loc="upper right", frameon=False,
              fontsize=9, title="KEGG Category", title_fontsize=10)

    fig.tight_layout()
    fig.savefig(out_base + ".png",  dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(out_base + ".tiff", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("[KEGG] Saved: %s.png / .tiff" % out_base)


# --- main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="GO + KEGG analysis for non-model hemipteran salivary gland proteome"
    )
    parser.add_argument("--emapper",   default=DEFAULT_EMAPPER,
                        help="Path to emapper.emapper.annotations")
    parser.add_argument("--annot",     default=DEFAULT_ANNOT,
                        help="Path to annotation_complete.tsv (for total protein count)")
    parser.add_argument("--obo",       default=OBO_PATH,
                        help="Path to go-basic.obo (downloaded if absent)")
    parser.add_argument("--min-depth", type=int, default=3,
                        help="Minimum GO term depth (default=3)")
    parser.add_argument("--top-go",    type=int, default=20,
                        help="Top N GO terms per category (default=20)")
    parser.add_argument("--top-kegg",  type=int, default=30,
                        help="Top N KEGG pathways for bubble chart (default=30)")
    args = parser.parse_args()

    total = get_total_proteins(args.annot)
    print("[INFO] Total proteins: %d" % total)

    # --- GO ---
    download_obo(args.obo)
    godict      = parse_obo(args.obo)
    emapper_data = parse_emapper(args.emapper)
    counters, go_info = build_go_frequency(emapper_data, godict, min_depth=args.min_depth)
    top_dfs     = top_n_dfs(counters, go_info, n=args.top_go)

    for ns, df in top_dfs.items():
        csv_out = "go_top%d_%s.csv" % (args.top_go, ns)
        df.to_csv(csv_out, index=False)
        print("[GO] Saved: %s" % csv_out)

    plot_go_distribution(top_dfs, out_base="go_distribution",
                         total=total, min_depth=args.min_depth)

    # --- KEGG ---
    pw_names = fetch_pathway_names()
    pw_cats  = fetch_pathway_categories()
    pw_df    = build_kegg_table(emapper_data, pw_names, pw_cats, total)

    plot_kegg_bar(pw_df,    top_n=20,          total=total)
    plot_kegg_bubble(pw_df, top_n=args.top_kegg, total=total)

    print("\n[DONE] All outputs saved to current directory:")
    print("  go_distribution.png / .tiff")
    print("  go_top%d_BP/MF/CC.csv" % args.top_go)
    print("  kegg_pathways.csv")
    print("  kegg_pathways_bar.png / .tiff")
    print("  kegg_pathways_bubble.png / .tiff")


if __name__ == "__main__":
    main()
