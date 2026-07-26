# Scripts do pipeline — versão genérica e comentada

> Material de apoio para o minicurso. Cada seção mostra a lógica central de uma etapa do pipeline, **generalizada** (nomes de variável genéricos, comentários explicando o porquê de cada parâmetro) e **resumida** — não é o código de produção completo do repositório, que tem bem mais tratamento de erro, retomada de execução e logging. Os scripts completos estão em `01_quality_assembly/`, `02_assembly_evaluation/`, `03_annotation/`, `04_functional_analysis/`, `05_secretome/` e `07_metagenomic_screen/`, caso alguém queira adaptar de verdade.
>
> Ordem: QC → montagem → avaliação → anotação → visualização → endossimbiontes (Camadas 1-2) → secretoma/efetores → **descoberta de patógeno e censo completo do microbioma (Camada 3, Seção 8)**.

---

## 1. Controle de qualidade e trimagem de reads

**Ferramentas:** FastQC, fastp, MultiQC. **Fonte:** `01_quality_assembly/01_qc_trimming.sh`.

```bash
#!/usr/bin/env bash
set -euo pipefail

R1="data/raw/${SAMPLE}_R1.fastq.gz"
R2="data/raw/${SAMPLE}_R2.fastq.gz"

# 1) QC das reads brutas -- gera relatório HTML por amostra + MultiQC agregado
fastqc --outdir results/qc/raw --threads "$THREADS" --extract "$R1" "$R2"
multiqc results/qc/raw --outdir results/qc/raw --force

# >>> CHECKPOINT manual: abrir o MultiQC antes de continuar.
#     Esperado: Phred >= Q28 na maior parte das posições, sem adaptador residual.

# 2) fastp: filtro de qualidade + remoção de adaptador + correção por overlap
fastp \
    --in1 "$R1" --in2 "$R2" \
    --out1 "data/trimmed/${SAMPLE}_R1.fastq.gz" \
    --out2 "data/trimmed/${SAMPLE}_R2.fastq.gz" \
    --qualified_quality_phred 20 \
    --unqualified_percent_limit 40 \
    --n_base_limit 5 \
    --length_required 50 \
    --detect_adapter_for_pe \
    --low_complexity_filter --complexity_threshold 30 \
    --correction \
    --thread "$THREADS" \
    --json fastp.json --html fastp.html

# 3) checkpoint automatizado de retenção de reads (>= 80% é o alvo)
python3 -c "
import json
d = json.load(open('fastp.json'))
before = d['summary']['before_filtering']['total_reads']
after  = d['summary']['after_filtering']['total_reads']
pct = 100 * after / before
print(f'Retencao: {pct:.1f}%')
assert pct >= 80, 'Retencao abaixo de 80% -- revisar parametros do fastp'
"
```

**Por que esses parâmetros?** `--detect_adapter_for_pe` evita ter que saber de antemão qual kit de biblioteca foi usado. `--low_complexity_filter` descarta reads tipo poli-A que não carregam informação. O checkpoint de retenção existe porque um fastp mal calibrado pode "limpar" agressivo demais e jogar fora metade dos dados sem ninguém perceber.

---

## 2. Montagem *de novo* — Trinity, CD-HIT-EST, TransDecoder

**Ferramentas:** Trinity, CD-HIT-EST, TransDecoder. **Fonte:** `01_quality_assembly/02_trinity_assembly.sh`.

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1) Montagem de novo -- sem genoma de referencia
Trinity \
    --seqType fq \
    --left "$TRIMMED_R1" --right "$TRIMMED_R2" \
    --SS_lib_type RF \
    --min_kmer_cov 2 \
    --min_contig_length 300 \
    --jaccard_clip \
    --max_memory 64G --CPU 16 \
    --output results/trinity_out
# --SS_lib_type RF   : biblioteca strand-specific: sem isso, transcritos de
#                      fita senso/antisenso podem ser fundidos incorretamente
# --jaccard_clip     : recomendado p/ transcriptomas gene-densos, evita
#                      contigs quimericos por genes vizinhos sobrepostos

TRINITY_FASTA="results/trinity_out/Trinity.fasta"

# 2) Reducao de redundancia -- Trinity superestima isoformas
cd-hit-est \
    -i "$TRINITY_FASTA" -o "$CDHIT_OUT" \
    -c 0.95 -n 8 -T 16 -M 0 -d 0
# -c 0.95  : agrupa transcritos com >=95% de identidade, mantem 1 representante
# -n 8     : word size recomendado pela documentacao do CD-HIT para c >= 0.90

# 3) Predicao de ORFs
TransDecoder.LongOrfs -t "$CDHIT_OUT" -m 100
# -m 100 : comprimento minimo de ORF em aa. O padrao da ferramenta e maior;
#          aqui foi reduzido de proposito para nao descartar peptideos
#          secretados curtos, relevantes para a hipotese de efetor salivar.

TransDecoder.Predict -t "$CDHIT_OUT" --single_best_only
# --single_best_only : mantem so a ORF de maior score por transcrito,
#                      evita contar a mesma proteina varias vezes a jusante
```

**Ponto didático:** repare que `-m 100` não é um valor "neutro" de bioinformática — ele já embute uma escolha ligada à pergunta biológica do projeto (não perder efetores pequenos). Vale sempre perguntar, ao ler um script de terceiros, *por que* aquele parâmetro tem aquele valor.

---

## 3. Avaliação de qualidade — N50, BUSCO

**Ferramentas:** TrinityStats.pl, seqkit, BUSCO. **Fonte:** `02_assembly_evaluation/03_stats_busco.sh`.

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1) Estatisticas basicas de montagem (gera a curva N10...N50)
TrinityStats.pl "$CDHIT_FASTA" | tee assembly_stats.txt

# 2) BUSCO -- completude via ortologos de copia unica conservados na linhagem
busco \
    --input "$CDHIT_FASTA" \
    --out "busco_${SAMPLE}" \
    --lineage_dataset insecta_odb10 \
    --mode transcriptome \
    --cpu 16 --force
# lineage_dataset: escolher o menor clado disponivel que contenha o
#                  organismo (aqui, Insecta, porque Hemiptera especifico
#                  nao estava disponivel no banco usado)
# mode transcriptome: avalia o FASTA de nucleotideos; existe tambem o modo
#                      'proteins', que usaria o .pep do TransDecoder
```

> **Nota de interpretação (tecido específico):** um transcriptoma de glândula salivar — um único tecido, não o corpo inteiro — é esperado que tenha completude BUSCO mais baixa e mais duplicação do que um transcriptoma de corpo inteiro, porque isoformas alternativas inflam a contagem de "duplicado" e genes não expressos naquele tecido específico contam como "missing". Isso não é sinal de montagem malfeita — é biologia.

---

## 4. Anotação funcional — DIAMOND, TaxonKit, eggNOG-mapper, Pfam

**Ferramentas:** DIAMOND, TaxonKit, eggNOG-mapper, HMMER. **Fonte:** `03_annotation/auto_annotate.py`.

```bash
# 1) Busca por similaridade contra o NCBI NR (proteinas)
diamond blastp \
    --db nr.dmnd --query proteins.fa --out diamond_nr.tsv \
    --outfmt 6 qseqid sseqid pident length mismatch gapopen \
               qstart qend sstart send evalue bitscore stitle \
    --evalue 1e-5 --max-target-seqs 1 --id 30 --query-cover 50 \
    --threads "$THREADS" --sensitive

# 2) Classificacao taxonomica dos organismos dos melhores hits
taxonkit name2taxid --data-dir "$TAXDUMP" organism_names.txt > name2taxid.tsv
taxonkit lineage    --data-dir "$TAXDUMP" taxids.txt         > lineage_raw.tsv
# usar sempre a lineage COMPLETA (nao a reformatada por ranks) como fonte
# de verdade para flags como is_eukaryote/is_fungi -- a versao reformatada
# frequentemente nao contem o token do reino p/ muitos taxons (ver Secao 6)

# 3) Ortologia funcional -- GO, KEGG, COG, CAZy
emapper.py \
    -i proteins.fa --itype proteins \
    -o emapper --data_dir "$EGGNOG_DB" --cpu "$THREADS" --override

# 4) Dominios proteicos conservados
hmmscan \
    --cpu "$THREADS" --tblout pfam_hits.tbl --domtblout pfam_domhits.tbl \
    -E 1e-5 --domE 1e-5 \
    Pfam-A.hmm proteins.fa
```

```python
# Parsing do eggNOG-mapper -- SEMPRE pelo header real (#query), nunca por
# indice de coluna hardcoded. Um bug real deste projeto foi ler eggnog_og
# do indice errado (seed_ortholog em vez de eggNOG_OGs) porque a coluna
# certa mudou de posicao entre versoes do eggNOG-mapper.
def parse_emapper(path):
    rows = {}
    with open(path) as f:
        header = None
        for line in f:
            if line.startswith("#query"):
                header = line.lstrip("#").rstrip("\n").split("\t")
                continue
            if line.startswith("#") or not header:
                continue
            parts = line.rstrip("\n").split("\t")
            row = dict(zip(header, parts))
            rows[row["query"]] = {
                "go_terms": row.get("GOs", ""),
                "kegg_ko":  row.get("KEGG_ko", ""),
                "eggnog_og": row.get("eggNOG_OGs", ""),
            }
    return rows
```

**Lição real do projeto:** o bug do índice hardcoded (`parts[1]` em vez de `parts[4]`) deixou GO e KEGG vazios em toda a tabela de anotação por semanas, sem erro nenhum — o script rodava, só produzia dado errado silenciosamente. Ler por nome de coluna, não por posição, é a defesa mais barata contra isso.

---

## 5. Visualização — figuras de anotação, GO/KEGG e QC de montagem

**Ferramentas:** matplotlib (Python). **Fontes:** `04_functional_analysis/plot_annotation.py`, `plot_assembly_qc.py`, `go_kegg_analysis.py`.

Padrão comum aos três scripts: carregar contagens já resumidas (não recalcular do zero a cada plot), usar paleta colorblind-safe fixa, e sempre salvar em PNG (300 dpi, para Word/slides) e TIFF (para submissão a periódico).

```python
import matplotlib
matplotlib.use("Agg")           # backend sem display -- roda em servidor
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "Arial", "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,  # menos "tinta", mais dado
})

# Exemplo generico: barra horizontal com rotulo de percentual embutido
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(labels, values, color="#2C7BB6", zorder=3)
for i, v in enumerate(values):
    ax.text(v / 2, i, f"{100*v/total:.1f}%", va="center", ha="center",
            color="white", fontweight="bold")
ax.grid(axis="x", color="#e0e0e0", lw=0.5, zorder=0)  # grid atras das barras

for ext, dpi in [("png", 300), ("tiff", 300)]:
    fig.savefig(f"figura.{ext}", dpi=dpi, bbox_inches="tight", facecolor="white")
```

O `go_kegg_analysis.py` tem uma peça a mais que vale citar: ele baixa e cacheia localmente o `go-basic.obo` (dicionário de termos GO) e a hierarquia KEGG via API REST (`https://rest.kegg.jp`), com retry exponencial em caso de erro 403 (a API do KEGG limita requisições por segundo). Cachear esse tipo de dado externo evita bater na API de novo toda vez que a figura é refeita.

---

## 6. Triagem de endossimbiontes (sem metagenômica dedicada)

**Ferramentas:** pandas (Python), reaproveitando a anotação já gerada. **Fonte:** `07_metagenomic_screen/01_taxonomic_summary.py`.

```python
import re
import pandas as pd

SYMBIONT_PATTERNS = {
    "Sulcia":  re.compile(r"sulcia",  re.I),
    "Sodalis": re.compile(r"sodalis", re.I),
}

annot = pd.read_csv("annotation_complete.tsv", sep="\t", dtype=str)

rows = []
for label, pattern in SYMBIONT_PATTERNS.items():
    mask = (
        annot["diamond_title"].str.contains(pattern, na=False)
        | annot["source_organism"].str.contains(pattern, na=False)
        | annot["lineage"].str.contains(pattern, na=False)
    )
    hits = annot[mask].copy()
    hits["symbiont_candidate"] = label
    rows.append(hits)

symbiont_hits = pd.concat(rows, ignore_index=True)
symbiont_hits.to_csv("sulcia_sodalis_hits.tsv", sep="\t", index=False)
```

**Por que isso funciona sem sequenciamento metagenômico dedicado:** quando um simbionte é altamente expresso, seus transcritos "vazam" para dentro de bibliotecas de RNA-seq de tecidos vizinhos — é um fenômeno já documentado para *Buchnera* em transcriptomas de afídeo. Então basta filtrar a anotação taxonômica que a gente já tinha gerado (Seção 4), procurando pelo nome do gênero esperado. É um atalho legítimo quando a pergunta é dirigida — não substitui uma triagem metagenômica completa se a pergunta for "existe *qualquer* microrganismo aqui que eu não esperava".

---

## 7. Predição de secretoma (concluído — TMbed substituiu SignalP6/TMHMM)

**Ferramentas:** TMbed (protein language model, único passo faz peptídeo sinal + hélice TM). **Fonte:** `05_secretome/secretome_predict.py`. SignalP6/TMHMM nunca foram instalados (licença DTU nunca obtida, indisponíveis via bioconda) — substituídos por TMbed, que roda 100% local sem login. Resultado real: 1.171 proteínas (9,4%) no secretoma clássico.

```bash
# Peptideo sinal -- proteina tem sequencia de exportacao?
signalp6 --fastafile proteins.fa --output_dir signalp_out \
          --organism eukarya --format txt --mode fast

# Helices transmembrana -- proteina fica ancorada na membrana?
tmhmm --short proteins.fa > tmhmm_results.txt
```

```python
# Filtro do secretoma classico: peptideo sinal presente E no maximo
# 1 helice transmembrana (mais que isso, a proteina provavelmente fica
# ancorada na membrana em vez de ser secretada para fora da celula)
def is_classical_secretome(has_signal_peptide, tm_helix_count):
    return has_signal_peptide and tm_helix_count <= 1
```

**Por que essa regra de corte:** uma proteína pode ter peptídeo sinal e mesmo assim não ser secretada de verdade — se ela tem várias hélices transmembrana, é mais provável que fique presa na membrana plasmática. O corte em "≤ 1 hélice" é o critério padrão da literatura para secretoma clássico, e é exatamente esse filtro que vai transformar a lista de "candidatos plausíveis" da Seção 3.5 do artigo numa lista curta e defensável de efetores candidatos.

---

## 8. Descoberta de patógeno e censo completo do microbioma (Camada 3)

**Ferramentas:** hmmfetch/hmmscan (HMMER), DIAMOND, bowtie2+samtools, pandas. Executado via comandos diretos durante a sessão de análise (não como scripts numerados reutilizáveis, diferente das seções 1-7 — ver Known Issues do README). Motivação: a pergunta biológica mudou de "confirmar os endossimbiontes esperados" para "existe um patógeno (vírus/fungo/bactéria) causando o amarelão?" — isso muda a ordem de prioridade e exige testar, não só descrever.

```bash
# 1) Extrair só os perfis HMM de RdRp (RNA-polimerase dependente de RNA) do
#    banco Pfam-A ja instalado -- evita baixar um banco viral dedicado do
#    zero. Os 31 codigos de acesso foram conferidos direto no arquivo real
#    (grep), nao de memoria -- Pfam versiona os codigos (ex. PF00680.26) e
#    hmmfetch falha silenciosamente se a versao nao bater.
hmmfetch -f Pfam-A.hmm rdrp_accessions.txt > rdrp_subset.hmm

# 2) Escanear as proteinas TransDecoder ja existentes contra esse subconjunto
hmmscan --domtblout rdrp_hits.domtbl rdrp_subset.hmm proteins.pep

# 3) Confirmar cada hit com RdRp por uma segunda fonte independente:
#    similaridade de sequencia contra um banco viral dedicado (nao o NR
#    generico, mais sensivel para virus divergentes)
diamond blastx -q contigs.fasta -d viral_refseq.dmnd -o viral_hits.tsv
```

```python
# 4) Confirmacao/refutacao de patogeno especifico por mapeamento
#    GENOMA INTEIRO (nao so 1 hit de proteina) -- e o mesmo principio de
#    Kraken2/mapeamento competitivo usado em metagenomica de verdade,
#    aplicado a um alvo especifico em vez de um banco generico
import subprocess
subprocess.run(["bowtie2", "-x", "ref_index", "-1", "reads_R1.fq.gz",
                 "-2", "reads_R2.fq.gz", "-S", "mapped.sam", "--no-unal"])
# depois: samtools depth -a --> breadth = % de posicoes com profundidade > 0
# CRITERIO DE REFUTACAO: se quase todas as poucas posicoes cobertas caem
# dentro de um operon de rRNA (conferido contra o GFF3 real do genoma),
# e cross-mapping de uma regiao universalmente conservada, nao presenca
# real do organismo -- foi exatamente o que aconteceu com Xylella/fitoplasma
# neste projeto (breadth < 0,3% em ambos, ~100% do sinal em rRNA).
```

**Por que caracterizar TUDO antes de inferir:** a tentação natural é ir direto testar os organismos que alguem ja suspeitava (aqui, Xylella e fitoplasma, ja sinalizados numa sessao anterior). Isso deixa um ponto cego real: dos 540 hits de Bacteria da anotacao, so uns 60 tinham sido olhados antes desta rodada. Quebrar TODOS os hits por genero (mesma logica de `groupby` + `value_counts` do pandas usada na Secao 6) e o que revelou, por exemplo, 88 hits de *Herbaspirillum* (endofito de gramineas, nunca mencionado antes) -- so depois desse censo completo faz sentido perguntar "e algum desses um candidato a causador de doenca?".

**Por que testar em vez de so descrever:** um hit de 45-70% de identidade a uma unica proteina (o que a Secao 6 faz) e fraco -- pode ser coincidencia de dominio conservado. Mapear TODOS os reads brutos contra o genoma de referencia inteiro, e checar ONDE exatamente as poucas posicoes cobertas caem (gene especifico vs. rRNA universal), e um teste muito mais rigoroso -- e foi o que permitiu refutar (nao so "nao confirmar") os dois leads que existiam.

---

## Referência — onde está cada script completo

| Etapa | Script completo | Linhas |
|---|---|---|
| QC/trimagem | `01_quality_assembly/01_qc_trimming.sh` | 247 |
| Montagem (Trinity/CD-HIT/TransDecoder) | `01_quality_assembly/02_trinity_assembly.sh` | 284 |
| Avaliação (stats/BUSCO) | `02_assembly_evaluation/03_stats_busco.sh` | 325 |
| Anotação funcional | `03_annotation/auto_annotate.py` | 673 |
| Correção do bug de merge | `03_annotation/07_fix_annotation_merge.py` | 208 |
| Figura de anotação | `04_functional_analysis/plot_annotation.py` | 160 |
| Figura de QC de montagem | `04_functional_analysis/plot_assembly_qc.py` | 182 |
| GO/KEGG | `04_functional_analysis/go_kegg_analysis.py` | 573 |
| Endossimbiontes (Camadas 1-2) | `07_metagenomic_screen/01_taxonomic_summary.py` + `04_cross_validate_endosymbionts.py` | 177 + ~150 |
| Secretoma | `05_secretome/secretome_predict.py` | 829 |
| Efetores/toxinas | `06_effector_prioritization/effector_candidates.py` | — |
| Camada 3 (patógeno + censo microbioma) | Executado via comandos diretos, sem script numerado permanente — ver Seção 8 e README "Known Issues" | — |
