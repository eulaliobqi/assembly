# Transcriptoma de novo da glândula salivar de *Mahanarva spectabilis* (Hemiptera: Cercopidae): candidatos a efetores fitotóxicos e endossimbiontes associados à síndrome do "amarelão" em pastagens

**Eulalio Santos¹\*, [Coautores a definir]**

¹Departamento de Biologia Geral / Departamento de Bioquímica e Biologia Molecular, Universidade Federal de Viçosa (UFV), Viçosa, MG 36570-900, Brasil

\*Correspondência: eulalio.santos@ufv.br

> **Nota:** este documento é atualizado incrementalmente à medida que os módulos de análise avançam (ver [Seção 6 — Status das Análises](#6-status-das-análises--próximas-etapas) para o estado atual). Todos os 13 módulos computacionais planejados estão concluídos; passou por uma auditoria de integridade completa (dados vs. arquivos-fonte, servidor vs. local, revisão de código) em 2026-08-30/31, sem número fabricado encontrado (item 17). Última atualização: 2026-08-31.

---

## Resumo / Abstract

*Mahanarva spectabilis* (cigarrinha-das-pastagens, Hemiptera: Cercopidae) é uma das principais pragas de pastagens de *Brachiaria*/*Urochloa* no Brasil, causando o sintoma conhecido como "amarelão": clorose progressiva e secamento foliar ao redor dos pontos de alimentação, com forte impacto na capacidade de suporte de pastagens. Apesar da relevância econômica, nenhum estudo até o momento identificou quimicamente o(s) composto(s) responsável(is) pela fitotoxemia, e a contribuição de microrganismos associados ao inseto (endossimbiontes obrigatórios, possíveis patógenos vetorados) permanece pouco explorada nesta espécie. Aqui apresentamos a montagem de novo e anotação funcional completa do transcriptoma da glândula salivar de *M. spectabilis* (Trinity: 90.344 genes / 103.560 transcritos; CD-HIT-EST 95%; TransDecoder: 12.445 proteínas; BUSCO insecta_odb10: C:96,2%), e iniciamos uma investigação transcriptômica dirigida a duas hipóteses complementares sobre a origem do amarelão: (i) toxinas/efetores salivares fitotóxicos secretados durante a alimentação xilemática, e (ii) contribuição de microrganismos associados à glândula/hospedeiro. A triagem taxonômica das anotações revelou **57 proteínas com alta identidade (~99%) a *Candidatus* Karelsulcia muelleri e 1 proteína a um simbionte *Sodalis*-like de *Philaenus spumarius***, consistente com o padrão de endossimbiose dupla obrigatória descrito para cigarrinhas-das-pastagens sul-americanas próximas; uma segunda camada de classificação estrutural independente (Whokaryote+Tiara) confirmou 3 desses candidatos como procariotos (0 discordâncias), com os demais fora do alcance de avaliação da ferramenta. A predição de secretoma clássico (TMbed) identificou 1.171 proteínas secretadas (9,4%), das quais **35 são candidatos priorizados a efetor/toxina salivar** por combinarem secreção com termos/domínios associados a fitotoxicidade em outros Hemiptera (proteases e carboxipeptidases tipo veneno, peptídeos salivares secretados, mucinas, fosfolipases, domínios EF-hand/Ca-binding, lacase). Uma anotação dbCAN dedicada, mais sensível que a anotação CAZy padrão, identificou adicionalmente 15 proteínas com domínios GH28/GH5 (celulases/pectinases), embora nenhuma esteja no secretoma clássico. Numa terceira camada de triagem dirigida diretamente à pergunta "algum patógeno causa o amarelão?", caracterizamos o microbioma completo (540 hits de Bacteria e 256 de Fungi, agrupados por gênero) e conduzimos busca dirigida por vírus (domínio RdRp), confirmação/refutação genoma-inteira de *Xylella*/fitoplasma por mapeamento de reads brutos, e varredura por genes de toxina microbiana. **Nenhum patógeno causador do amarelão foi confirmado**: *Xylella* e fitoplasma foram diretamente refutados (cobertura genoma-inteira <0,3%, sinal residual majoritariamente explicado por rRNA conservado), os vírus confirmados com alta confiança são todos linhagens específicas de artrópode sem precedente fitopatogênico, e nenhum gene de fitotoxina clássica foi encontrado. Por eliminação, esse resultado reforça a hipótese de efetor/toxina salivar do próprio inseto como explicação mais bem sustentada pelos dados atuais. Este trabalho fornece o primeiro recurso transcriptômico de larga escala para a glândula salivar de *M. spectabilis* e um arcabouço analítico replicável, com uma lista concreta e priorizada de candidatos, para testar hipóteses sobre fitotoxemia e simbiose em Cercopidae.

**Palavras-chave:** *Mahanarva spectabilis*, cigarrinha-das-pastagens, amarelão, transcriptoma de novo, efetores salivares, endossimbiontes, *Candidatus* Sulcia muelleri, fitotoxemia

---

## 1. Introdução

*Mahanarva spectabilis* (Distant, 1909) pertence ao grupo das "cigarrinhas-das-pastagens" (Hemiptera: Cercopidae), que inclui as principais pragas de gramíneas forrageiras neotropicais, entre elas os gêneros *Mahanarva*, *Deois*, *Notozulia* e *Zulia* (Hernandez et al., 2022). Populações de 25–50 adultos/m² podem reduzir a taxa de lotação de pastagens em 26–33% (Holmann & Peck, 2002, apud Hernandez et al., 2022), tornando essas cigarrinhas uma das pragas de maior impacto econômico na pecuária brasileira baseada em *Brachiaria*/*Urochloa*.

O dano característico, popularmente conhecido como "amarelão" ou "queima do capim", manifesta-se como clorose acropetal em ninfas de estádios avançados e manchas cloróticas esbranquiçadas ao redor dos pontos de sucção em adultos, evoluindo para necrose e secamento foliar sob alta infestação (Valério et al., 2001; Sotelo & Cardona, 2001; Thompson & González, 2005). Diferentemente das cigarrinhas floema-alimentadoras (Cicadellidae, ex. *Empoasca* spp.), cujo dano ("hopperburn") resulta de um padrão específico de ferimento vascular mais resposta da planta (Backus, Serrano & Ranger, 2005), as cigarrinhas-das-pastagens (Cercopoidea) alimentam-se estritamente de xilema, formando uma bainha salivar contínua ao redor do vaso (Cornara et al., 2018). O consenso agronômico atribui o amarelão a substâncias fitotóxicas presentes na saliva injetada durante a alimentação xilemática, possivelmente incluindo uma fração que se coagula nos tecidos (bloqueio vascular local) e uma fração solúvel translocada a distância (necrose sistêmica). Ainda assim, **nenhum estudo publicado identificou molecularmente essa(s) toxina(s)** até o momento.

Um grupo de pesquisa da UFV (Departamento de Bioquímica e Biologia Molecular) vem caracterizando por proteômica os componentes da saliva e da espuma protetora de *M. spectabilis*: Monteiro (2019) identificou candidatos a efetor, incluindo ácidos graxos de cadeia longa, na saliva de ninfas/adultos alimentados em diferentes forrageiras; Rinaldi (2021) investigou diretamente componentes moleculares da toxina e da espuma salivar; Rinaldi et al. (2026) caracterizaram estruturalmente proteínas de espuma de ninfas via LC-MS/MS e modelagem AlphaFold. O presente transcriptoma foi concebido como um recurso complementar em nível de transcrito para essa mesma pergunta biológica, permitindo (i) uma busca sistemática, guiada por anotação funcional e predição de secretoma, por candidatos a efetor/toxina salivar, e (ii) uma investigação, ainda inédita para o gênero *Mahanarva*, sobre a contribuição de microrganismos associados ao inseto.

Quanto à segunda hipótese: cigarrinhas-espumantes (superfamília Cercopoidea) são classicamente conhecidas por hospedar endossimbiontes bacterianos obrigatórios de complementação nutricional, tipicamente *Candidatus* Sulcia muelleri (Bacteroidota) associado a um segundo simbionte, *Candidatus* Zinderia insecticola (Betaproteobacteria) ou, em algumas linhagens, um substituto evolutivo *Sodalis*-like (McCutcheon & Moran, 2007; Bennett & Moran, 2013; Koga & Moran, 2014). Foieri et al. (2022) confirmaram por 16S rRNA a presença de *Sulcia* em três cigarrinhas-das-pastagens sul-americanas filogeneticamente próximas de *Mahanarva* (*Notozulia entreriana*, *Deois mourei*, *Deois knoblauchii*), tornando a presença desse simbionte em *M. spectabilis* uma expectativa forte a priori. Adicionalmente, por serem exclusivamente xilema-alimentadoras, cigarrinhas-das-pastagens são, em princípio, vetores mecanisticamente plausíveis de patógenos limitados ao xilema (ex. *Xylella fastidiosa*, já confirmada em cigarrinhas-espumantes europeias (Cornara et al., 2017), mas biologicamente incompatíveis como vetores de fitoplasmas (limitados ao floema).

Este artigo tem como objetivo (1) documentar a montagem e anotação funcional completa do transcriptoma da glândula salivar de *M. spectabilis*; (2) reportar os achados iniciais da triagem taxonômica quanto a endossimbiontes/microrganismos associados; e (3) estabelecer o arcabouço metodológico, em execução incremental, para a priorização de candidatos a efetor/toxina salivar relacionados ao amarelão.

---

## 2. Materiais e Métodos

### 2.1 Material biológico e sequenciamento

Glândulas salivares de *M. spectabilis* foram dissecadas para extração de RNA total e sequenciamento Illumina paired-end (detalhes de biblioteca/plataforma/número de réplicas a confirmar e incluir nesta seção antes da submissão; ver `data/README.md`). Os arquivos FASTQ brutos não estão incluídos neste repositório devido ao tamanho; serão depositados no NCBI SRA por ocasião da publicação.

### 2.2 Montagem de novo e avaliação de qualidade

Reads foram avaliados com **FastQC v0.12.1** e **MultiQC v1.21** (relatório agregado, pré e pós-trimming) e filtrados/aparados com **fastp v0.23.4** (Q≥20, comprimento mínimo 50 bp). A montagem de novo foi feita com **Trinity v2.15.2** (`--SS_lib_type RF`, `--min_kmer_cov 2`, `--min_contig_length 300`, `--jaccard_clip`). Transcritos redundantes foram agrupados com **CD-HIT-EST v4.8.1** (`-c 0.95`, identidade de 95% sobre a sequência mais curta; `-n 8`, `-M 0`). ORFs foram preditas com **TransDecoder v5.7.1** (`TransDecoder.LongOrfs -m 100` seguido de `TransDecoder.Predict --single_best_only`, retendo o melhor ORF por transcrito, mínimo 100 aminoácidos). A completude da montagem foi avaliada com **BUSCO v6.0.0** (linhagem `insecta_odb10`, criada em 2024-01-08, 1.367 genes ortólogos de cópia única, modo `euk_tran`; dependências internas hmmsearch 3.4 e metaeuk 7.bba0d80) e estatísticas gerais com `TrinityStats.pl` (empacotado com o Trinity) e **seqkit v2.13.0**.

### 2.3 Anotação funcional

Proteínas preditas foram anotadas por: (i) **DIAMOND v2.1.9** BLASTp contra o NCBI NR (`--evalue 1e-5 --max-target-seqs 1`); (ii) classificação taxonômica dos melhores hits via **TaxonKit v0.15.1** (lineage completo, não a versão reformatada por ranks, para evitar perda de classificação — ver Seção 5, Problemas Conhecidos); (iii) **eggNOG-mapper v2.1.12** (GO, KEGG, COG, CAZy); (iv) **HMMER v3.4** (`hmmscan`) contra o banco **Pfam-A** (domínios proteicos). Todas as fontes foram integradas em uma tabela única (`results/annotation_complete.tsv`, `03_annotation/auto_annotate.py` + `07_fix_annotation_merge.py`).

### 2.4 Quantificação de expressão

A abundância de transcritos foi quantificada com **Salmon v1.10.3** (modo de mapeamento seletivo contra o transcriptoma montado, TPM por transcrito; `expression/salmon-quant.sf`), usada como camada de evidência adicional na priorização de candidatos a efetor (Seção 2.6) e na extração de candidatos a endossimbionte (Seção 2.7).

### 2.5 Predição de secretoma clássico

Proteínas preditas foram submetidas a predição conjunta de peptídeo sinal e segmento transmembrana com **TMbed v1.0.2** (Bernhofer & Rost, 2022; torch v2.13.0, transformers v4.57.6), um preditor baseado em embeddings de protein language model (ProtT5), classificando como "secretoma clássico" as proteínas com peptídeo sinal presente E ≤1 segmento transmembrana (`05_secretome/secretome_predict.py`). TMbed substituiu SignalP6/TMHMM, cuja licença acadêmica DTU nunca foi obtida neste ou em outros dois projetos do laboratório (`RLPredictiOme`, `caracterization-trypsin`); TMbed é instalável via `pip`, roda localmente sem necessidade de conta/licença, e não está disponível via bioconda/conda-forge sob nenhum nome de pacote. **Status: concluído.**

### 2.6 Priorização de candidatos a efetor/toxina salivar

Os candidatos foram filtrados por: (i) status de secretado (Seção 2.5); (ii) presença de termos/domínios funcionais associados a fitotoxicidade em Hemiptera na literatura (proteases tipo veneno, peptídeos salivares secretados, mucinas, lacases, fosfolipases A2/B, domínios EF-hand/Ca-binding, CAZymes GH28/GH5 via dbCAN dedicado, com correspondência por expressão regular sensível a subfamílias com sufixo, ex. `GH5_12`) e (iii) nível de expressão (TPM), via `06_effector_prioritization/effector_candidates.py`. O ranking é aditivo (número de termos curados correspondentes, depois TPM), não inferido por ML. **Status: concluído.**

### 2.7 Triagem de endossimbiontes, patógenos e microbioma associado (Camadas 1–3)

A triagem foi conduzida em três camadas progressivas. **Camada 1** — reaproveitamento das classificações taxonômicas DIAMOND/lineage já geradas na anotação funcional (`07_metagenomic_screen/01_taxonomic_summary.py`), extraindo proteínas com hit em *Sulcia*/*Zinderia*/*Sodalis*-like e sinalizando separadamente hits de baixa prioridade (*Xylella*, fitoplasma). **Camada 2** — confirmação independente via classificação estrutural (baseada em conteúdo gênico, não em similaridade de sequência a um banco de referência — portanto não circular em relação à Camada 1) dos contigs montados com **Whokaryote v1.1.2** + **Tiara v1.0.3** (Pronk & Medema, 2022; Karlicki et al., 2022), cruzada com a Camada 1 via `07_metagenomic_screen/04_cross_validate_endosymbionts.py`.

**Camada 3** — motivada pela pergunta biológica direta "algum patógeno (vírus, fungo ou bactéria) causa ou co-causa o amarelão?", usando desta vez o FASTQ bruto (`gland-saliv_{1,2}.fq.gz`, 86.697.028 pares de reads) diretamente, disponível no diretório de dados brutos do servidor (`/home/eulalio/Gland-saliv-cigarrinha`) e não apenas os contigs/proteínas já montados:

- **Censo completo do microbioma bacteriano e fúngico**: todos os 540 hits com melhor correspondência em Bacteria e todos os 256 hits em Fungi (coluna `source_organism` de `results/annotation_complete.tsv`) foram agrupados por gênero/espécie — não apenas os candidatos já pré-selecionados em sessões anteriores — para obter um retrato completo do que está presente, não só dos candidatos já suspeitos.
- **Descoberta viral dirigida por domínio RdRp**: 31 famílias HMM de RNA-polimerase dependente de RNA (RdRp) foram extraídas do banco Pfam-A já instalado localmente (`hmmfetch`, HMMER v3.4) e usadas para escanear as 12.445 proteínas TransDecoder (`hmmscan`), complementado por **DIAMOND v2.1.9** `blastx` dos contigs montados contra o banco viral RefSeq da NCBI (722.107 proteínas). Os 30 hits virais já existentes na anotação DIAMOND/NR original (Seção 3.3, tabela) foram reclassificados por família taxonômica real (consulta à taxonomia NCBI) para distinguir vírus genuínos de elementos genômicos do tipo retrotransposon (Metaviridae, Polintoviridae) erroneamente rotulados como "vírus" pela nomenclatura do banco de referência.
- **Confirmação/refutação direcionada de Xylella/fitoplasma por mapeamento genoma-inteiro**: os reads brutos (86.697.028 pares) foram mapeados com **Bowtie2 v2.5.5** contra os genomas de referência completos de *Xylella fastidiosa* subsp. *multiplex* (GCF_042238405.1) e do fitoplasma Aster Yellows (NC_007716.1 + 4 plasmídeos), com cálculo de amplitude (*breadth*) e profundidade de cobertura genoma-inteira e localização das posições cobertas via anotação GFF3 real — um critério de confirmação muito mais rigoroso que a identidade de um único hit de proteína.
- **Busca por genes de toxina/virulência microbiana**: varredura por palavra-chave (toxina, hemolisina, RTX, fosfolipase, fator de virulência, etc.) nas colunas `diamond_title`, `eggnog_desc` e `pfam_domains` de todos os hits de Bacteria e Fungi, independente do organismo de origem — abordagem complementar à busca organismo-primeiro das Camadas 1–2.

Bancos de dados baixados para esta camada (viral RefSeq NCBI, genomas de referência Xylella/fitoplasma) foram usados e removidos do servidor após a análise, mantendo apenas as tabelas de resultado. **Status: concluído** (as três camadas).

Como validação adicional do candidato a endossimbionte *Sulcia* (Camada 1), o gene GroEL foi alinhado contra sequências de referência de *Candidatus* Karelsulcia muelleri e um outgroup de Bacteroidetes de vida livre (*Sodalis glossinidius*, *Bacteroides* sp.), e submetido a inferência filogenética de máxima verossimilhança com **IQ-TREE v3.1.1** (ModelFinder para seleção automática de modelo + bootstrap ultrarrápido, 1000 réplicas; Hoang et al., 2018), via `08_metagenomic_deep/`.

### 2.8 Anotação CAZy dedicada

A anotação CAZy do eggNOG-mapper (Seção 2.3) cobre apenas 1,4% das proteínas e não identificou nenhum hit às famílias GH28/GH5 — resultado de baixa sensibilidade conhecida, não necessariamente ausência real dessas atividades. Uma anotação dbCAN dedicada foi executada com **`run_dbcan` v5.2.9** (DIAMOND v2.2.4 + dbCAN-HMM/pyhmmer v0.12.1 + dbCAN-sub contra o banco de dados dbCAN real; Zheng et al., 2023), via `03_annotation/08_cazy_annotation.sh` + `09_merge_cazy.py`. **Status: concluído.**

### 2.9 Ferramentas, versões e ambientes

Tabela consolidada de todo o software usado neste trabalho, com a versão efetivamente instalada e executada (verificada por `conda list` no ambiente correspondente ou pelo cabeçalho do arquivo de saída da própria ferramenta — ver auditoria de integridade, Seção 6, item 17). Definições completas dos ambientes conda em `environment/*.yml`.

| Ferramenta | Versão | Etapa | Referência |
|---|---|---|---|
| FastQC | 0.12.1 | QC de reads (bruto/pós-trim) | Andrews, 2010 |
| fastp | 0.23.4 | Trimming de adaptador/qualidade | Chen et al., 2018 |
| MultiQC | 1.21 | Agregação de relatórios QC | Ewels et al., 2016 |
| Trinity | 2.15.2 | Montagem de novo | Grabherr et al., 2011; Haas et al., 2013 |
| CD-HIT-EST | 4.8.1 | Remoção de redundância (95% identidade) | Fu et al., 2012 |
| TransDecoder | 5.7.1 | Predição de ORF/proteína | Haas et al., 2013 |
| seqkit | 2.13.0 | Estatísticas de sequência | Shen et al., 2016 |
| BUSCO | 6.0.0 (`insecta_odb10`) | Completude da montagem | Manni et al., 2021 |
| DIAMOND | 2.1.9 (anotação/viral) / 2.2.4 (dbCAN) | BLASTp/BLASTx | Buchfink et al., 2021 |
| TaxonKit | 0.15.1 | Classificação taxonômica | Shen & Ren, 2021 |
| eggNOG-mapper | 2.1.12 | Anotação GO/KEGG/COG/CAZy | Cantalapiedra et al., 2021 |
| HMMER | 3.4 | Domínios Pfam, `hmmscan` RdRp | Eddy, 2011 |
| Salmon | 1.10.3 | Quantificação de expressão (TPM) | Patro et al., 2017 |
| TMbed | 1.0.2 | Predição de secretoma clássico | Bernhofer & Rost, 2022 |
| run_dbcan (dbCAN3) | 5.2.9 | Anotação CAZy dedicada | Zheng et al., 2023 |
| Whokaryote | 1.1.2 | Classificação estrutural euc./proc. | Pronk & Medema, 2022 |
| Tiara | 1.0.3 | Classificação estrutural euc./proc. | Karlicki et al., 2022 |
| Bowtie2 | 2.5.5 | Mapeamento genoma-inteiro (Xylella/fitoplasma) | Langmead & Salzberg, 2012 |
| IQ-TREE | 3.1.1 | Filogenia de máxima verossimilhança (GroEL) | Wong et al., 2025 |

---

## 3. Resultados

### 3.1 Montagem e avaliação de qualidade

| Métrica | Valor |
|---|---|
| Genes Trinity | 90.344 |
| Transcritos Trinity | 103.560 |
| Conteúdo GC | 34,21% |
| N50 (todos os transcritos) | 738 |
| Bases montadas totais | 68.986.692 |
| Proteínas TransDecoder (`--single_best_only`) | 12.445 |
| BUSCO (insecta_odb10, n=1.367) | C:96,2% [S:39,9%, D:56,3%], F:1,9%, M:1,9% |

[[FIG:assembly_qc_summary]]

### 3.2 Anotação funcional

Da tabela integrada (`results/annotation_complete.tsv`, 12.445 proteínas), 62,1% possuem domínio Pfam, 44,0% possuem termo GO e 42,6% possuem ortólogo KEGG (eggNOG-mapper). A coluna CAZy do eggNOG cobria apenas 1,4% das proteínas (175) e não encontrou nenhum hit às famílias GH28/GH5. A anotação dbCAN dedicada (Seção 2.8) elevou a cobertura para **468 proteínas (3,8%) com pelo menos uma família CAZy** e identificou **15 proteínas com chamada GH28 ou GH5\*** (celulases/pectinases classicamente associadas a efetores fitotóxicos de degradação de parede celular) — resultado que confirma a baixa sensibilidade da anotação CAZy do eggNOG e fornece novos candidatos reais para a Seção 3.6.

[[FIG:annotation_summary]]

A distribuição dos 20 termos GO mais frequentes (profundidade ≥ 3) reforça o perfil esperado de um tecido secretor metabolicamente ativo: entre os processos biológicos mais representados estão regulação de processo celular (25,6%) e processo metabólico primário (24,1%); entre as funções moleculares, ligação a composto heterocíclico (11,0%) e ligação a enzima (9,2%); entre os componentes celulares, organela intracelular (33,0%) e organela limitada por membrana (29,9%).

[[FIG:go_distribution]]

Entre os 12.445 proteínas com ortólogo KEGG atribuído, a via mais representada é "Metabolic pathways" (845 proteínas, 6,8%), seguida por "Biosynthesis of secondary metabolites" (388; 3,1%) e "Ribosome" (261; 2,1%). A predominância de vias metabólicas centrais e de categorias amplamente conservadas (Human Diseases, Other) nas posições intermediárias do ranking é esperada para eggNOG-mapper, cuja anotação usa como referência ortólogos humanos/modelo, e não indica especialização funcional exclusiva da glândula salivar.

[[FIG:kegg_pathways_bar]]

[[FIG:kegg_pathways_bubble]]

### 3.3 Distribuição taxonômica dos melhores hits e censo completo do microbioma

| Origem taxonômica | N proteínas | % |
|---|---|---|
| Eukaryota | 8.711 | 70,0% |
| Bacteria | 540 | 4,3% |
| Fungi | 256 | 2,1% |
| Viruses | 30 | 0,2% |
| Não classificado | 3.164 | 25,4% |

*Nota: as categorias Eukaryota/Fungi não são mutuamente exclusivas (uma proteína fúngica é, por definição, também eucariótica); a soma das categorias pode exceder 100%.*

**Censo completo de Bacteria (540 hits, todos agrupados por gênero — não apenas os pré-selecionados):**

| Categoria | N | Interpretação |
|---|---|---|
| *Gammaproteobacteria* sp. (não classificado) | 118 | Baixa resolução taxonômica, não permite inferência de espécie |
| *Herbaspirillum* spp. | 88 | Gênero clássico de endófito diazotrófico de gramíneas tropicais, **incluindo *Brachiaria*/*Urochloa*, o hospedeiro exato da cigarrinha** — provável material vegetal capturado via seiva de xilema ingerida, não é patógeno conhecido |
| *Chryseobacterium*/Flavobacteriaceae | 71 | Generalista ambiental/associado a inseto |
| Enterobacterales/*Enterobacter* | 59 | Generalista de microbiota de inseto e endófitos |
| *Candidatus* Karelsulcia muelleri | 57 | Endossimbionte obrigatório (Seção 3.4) |
| Outros gêneros singleton (ambiental diverso) | 47 | Dezenas de gêneros de solo/planta, 1–3 hits cada, sem padrão claro |
| *Klebsiella pneumoniae* | 31 | Oportunista comum, super-representado em bancos de referência (possível viés) |
| *Acinetobacter* spp. | 20 | Generalista/oportunista ambiental |
| Cyanobacteria | 18 | Provável origem vegetal/ambiental (fotossintética) |
| Patógenos humanos/aviários (*Salmonella*, *Shigella*, *Staphylococcus*, *Streptococcus pneumoniae* etc.) | 14 | Amplamente sequenciados no NR; hits singleton a genes conservados — **provável viés de banco de dados, biologicamente implausível** neste sistema |
| *Wolbachia* endosymbiont | 6 | Endossimbionte reprodutivo comum em artrópodes |
| Simbiontes marinhos (*Solemya*, *Thiodiazotropha*) | 6 | Hospedeiro impossível (moluscos marinhos) — confirma artefato de banco de dados |
| *Sodalis*-like symbiont | 1 | Co-simbionte (Seção 3.4) |
| *Xylella fastidiosa* subsp. *multiplex* | 1 | **Testado e refutado por mapeamento genoma-inteiro** (ver abaixo) |
| Fitoplasma Aster Yellows | 1 | **Testado e refutado por mapeamento genoma-inteiro** (ver abaixo) |
| *Pseudomonas syringae* pv. *actinidiae* | 1 | Patógeno real, mas de kiwi — hospedeiro errado, n=1, não testado (sinal fraco demais) |
| *Candidatus* Erwinia dacicola | 1 | Simbionte conhecido da mosca-da-azeitona — sistema hospedeiro diferente, n=1, provável hit espúrio |

**Censo completo de Fungi (256 hits, todos agrupados por gênero):**

| Categoria | N | Interpretação |
|---|---|---|
| Entomopatogênicos (*Entomophthora muscae* 96, *Neoconidiobolus* 26, *Massospora cicadina* 18, *Metarhizium* spp. 56) | 196 (76,6%) | Patógenos do próprio inseto — biologicamente plausíveis, irrelevantes para o amarelão (relevantes para controle biológico da cigarrinha) |
| *Erysiphe pulchra* | 15 | Fitopatógeno (oídio), mas ataca superfície foliar — mecanisticamente improvável para o sintoma de xilema do amarelão |
| *Fusarium* spp. (murcha vascular) | 8 | Único gênero fitopatogênico com plausibilidade mecânica (coloniza xilema), mas sinal fraco, não confirmado por fonte independente |
| Diversos gêneros singleton | 37 | Ambiental/saprófita comum, sem padrão |

**Censo viral (30 hits originais + descoberta dirigida por RdRp):** dos 30 hits virais da anotação original, a reclassificação taxonômica (NCBI) revelou que **12 (40%) não são vírus infecciosos**, e sim elementos genômicos móveis do próprio genoma do inseto rotulados como "vírus" pela nomenclatura do banco: *Halyomorpha halys* erranti-like virus 1 (10 hits; família Metaviridae — retrotransposon LTR tipo *errantivirus*) e *Megastigmus* wasp adintovirus (2 hits; Eupolintoviridae — elemento tipo Polinton/virófago). Dos **18 hits restantes que são vírus genuínos**: 4 são mycovírus (infectam os fungos já detectados acima — *Verticillium*, *Erysiphe*, *Magnaporthe*, *Leptosphaeria* — consistência interna do censo), e 14 são vírus de RNA associados a artrópodes sem precedente de fitopatogenicidade (Narnaviridae, Nodaviridae, Phasmaviridae, Jingmenvirus-like, Dicistroviridae, um vírus Orthomyxo-relacionado já descrito em Hemiptera). A busca dirigida por domínio RdRp (`hmmscan`, 31 famílias) confirmou por 2 fontes independentes (domínio + identidade BLASTx) 4 desses vírus genuínos: três com alta confiança — um Jingmenvirus-like (41,6% identidade a *Wuhan flea virus* NS5-like), um Nodaviridae-like (87,6% identidade a *Boolarra virus*) e um Dicistroviridae-like (69,8% identidade a *Drosophila C virus*/*Nilaparvata lugens C virus*) — e um quarto, Cypovirus-like (Reoviridae), com confiança média-alta (domínio RdRp muito forte, mas identidade de sequência baixa/divergente, 26,3%). **Busca dirigida pela família RdRp de Phytoreovirus (o grupo clássico de vírus de planta vetorado por Auchenorrhyncha) não teve nenhum hit em nenhum contig** — ausência notável dado o desenho do estudo.

**Busca por genes de toxina/virulência microbiana:** varredura por palavra-chave em toda a anotação de Bacteria+Fungi encontrou apenas sistemas toxina-antitoxina bacterianos intracelulares universais (RelE/RelB, VapBC, MazF — módulos de regulação de persistência/estresse presentes em praticamente toda bactéria de vida livre, sem relação com fitopatogenicidade) e uma fosfolipase de *Metarhizium anisopliae* (consistente com seu papel já conhecido como fungo entomopatogênico, não fitopatogênico). Nenhum gene de fitotoxina clássica (coronatina, tabtoxina, siringomicina, proteínas indutoras de necrose tipo NEP1) foi encontrado.

[[FIG:microbiome_census]]

[[FIG:pathogen_screening]]

### 3.4 Candidatos a endossimbionte

A extração dirigida de hits com correspondência a simbiontes conhecidos de Auchenorrhyncha identificou **57 proteínas com ~99% de identidade a *Candidatus* Karelsulcia muelleri**, incluindo genes housekeeping clássicos de simbiontes nutricionais (6-fosfofrutoquinase, GAPDH, chaperonina GroEL, enzima málica, fator de iniciação da tradução IF-2) — um padrão de expressão consistente com um simbionte metabolicamente ativo e não com contaminação aleatória. Foi identificada também **1 proteína com hit em simbionte *Sodalis*-like de *Philaenus spumarius*** (cigarrinha-das-pastagens europeia, mesma superfamília Cercopoidea). Esses achados são fortemente consistentes com o padrão de endossimbiose dupla obrigatória (*Sulcia* + *Zinderia*/*Sodalis*-like) já descrito para cigarrinhas-espumantes, incluindo três espécies sul-americanas próximas confirmadas por Foieri et al. (2022).

Dois hits de baixa confiança foram sinalizados separadamente: 1 proteína com 45,1% de identidade a *Xylella fastidiosa* (domínio genérico Bro-N, baixa especificidade) e 1 proteína com 70,0% de identidade a uma DNA polimerase parcial de fitoplasma "aster yellows". Diferentemente da versão anterior deste documento, esses dois leads **foram testados diretamente e refutados**: o mapeamento dos ~173 milhões de reads brutos contra os genomas de referência completos de *X. fastidiosa* subsp. *multiplex* e do fitoplasma Aster Yellows (Seção 2.7, Camada 3) produziu amplitude de cobertura genoma-inteira de apenas 0,28% e 0,17%, respectivamente — e **100% (fitoplasma) / 98,0% (Xylella) das poucas posições cobertas caem dentro de operons de rRNA 16S/23S** (confirmado via anotação GFF3 real posição-a-posição), a assinatura clássica de cross-mapping inespecífico de uma região universalmente conservada entre bactérias distantes, não presença real do patógeno. Os 1,97% restantes em Xylella caem num gene de protease S8 igualmente conservado e não-diagnóstico. Não há, portanto, nenhuma evidência de presença de *Xylella* ou fitoplasma neste material.

**Confirmação independente (Camada 2):** a classificação estrutural eucarioto/procarioto de Whokaryote+Tiara, que não depende de similaridade de sequência a um banco de referência, foi cruzada com os 60 candidatos da Camada 1 (57 *Sulcia*/*Sodalis*-like + 2 patógenos de baixa prioridade). Whokaryote só classifica contigs ≥5.000 pb — a maioria dos candidatos é composta por genes bacterianos únicos em transcritos Trinity curtos — de modo que apenas 3 candidatos puderam ser avaliados; os 3 foram classificados como procarioto (**concordantes**, 0 discordantes), e os 57 restantes ficaram como "não analisado" por limitação de cobertura da Camada 2, não como evidência contra a chamada da Camada 1 (`results/endosymbiont_candidates/endosymbionts_cross_validated.tsv`).

**Evidência adicional (Camada 3):** o perfil de GC dos 37 candidatos *Sulcia*/*Sodalis* com dados de expressão (mediana 24,9%) é significativamente menor que o do restante do transcriptoma eucariótico anotado (mediana 36,2%; Mann-Whitney p=8,1×10⁻²³), consistente com o genoma extremamente reduzido e rico em AT já descrito para *Sulcia* na literatura. A identidade de 99,4% a proteínas nomeadas de *Candidatus* Karelsulcia muelleri (GroEL, GAPDH) permanece a evidência mais direta de identidade de espécie.

[[FIG:blobplot_gc_tpm]]

**Uma tentativa de validação filogenética (GroEL, máxima verossimilhança + bootstrap ultrarrápido, `08_metagenomic_deep/`) não foi conclusiva**: mesmo após adicionar um outgroup de Bacteroidetes de vida livre, o candidato de *M. spectabilis* não se agrupou dentro do clado *Karelsulcia* com suporte estatístico adequado (bootstrap 49–72%, abaixo do limiar de 95% adotado como critério) — resultado reportado sem tentativas adicionais de reamostragem taxonômica para não distorcer o achado.

[[FIG:groel_phylogeny]]

### 3.5 Predição de secretoma clássico

A predição TMbed (Seção 2.5) classificou **1.238 proteínas (9,9%) com peptídeo sinal** e **1.171 proteínas (9,4%) como secretoma clássico** (peptídeo sinal presente E ≤1 segmento transmembrana; 67 proteínas excluídas por terem >1 segmento TM). Do secretoma clássico, 79,0% têm hit DIAMOND, 67,1% têm domínio Pfam, 51,0% têm termo GO e 37,7% têm ortólogo KEGG. As categorias COG mais representadas no secretoma clássico são função desconhecida (277), transdução de sinal (147), modificação pós-traducional/chaperonas (145) e transporte/metabolismo de carboidratos (89) (`results/secretome/secretome_report.txt`).

[[FIG:secretome_summary]]

### 3.6 Candidatos a efetor/toxina salivar (secretoma × termos curados × expressão)

A interseção do secretoma clássico com a lista curada de termos/domínios de efetor/toxina (Seção 2.6) produziu **35 candidatos** (`results/effector_candidates/effector_candidates_ranked.tsv`). Por categoria: domínios EF-hand/Ca-binding (16), mucinas (9), peptídeo/proteína salivar secretado (4), fosfolipase A2/B (2), protease tipo veneno (1), carboxipeptidase tipo veneno (1), dipeptidil peptidase 4 tipo veneno (1) e lacase (1). Os candidatos de maior expressão incluem uma proteína salivar secretada (melhor hit DIAMOND: *Triatoma infestans*, TPM=52,3), uma protease tipo veneno (melhor hit: *Macrosteles quadrilineatus*, cigarrinha da mesma ordem Hemiptera, TPM=6,9) e uma carboxipeptidase de serina tipo veneno. Nenhum dos 15 hits GH28/GH5 do dbCAN dedicado (Seção 3.2) permaneceu na lista final por não estarem simultaneamente no secretoma clássico — achado que qualifica, sem invalidar, a hipótese de celulases/pectinases secretadas como efetores.

[[FIG:effector_candidates]]

---

## 4. Discussão

Os resultados de montagem e anotação situam este transcriptoma como um recurso robusto e comparável a outros esforços de sequenciamento de novo em Hemiptera não-modelo (BUSCO >95%, ampla cobertura de anotação funcional). O achado mais imediatamente conclusivo é a confirmação, em nível de transcrito, da endossimbiose dupla obrigatória esperada para Cercopoidea. Os 57 hits de *Sulcia* com identidade ~99% em genes de biossíntese/metabolismo central deixam pouca dúvida quanto à presença ativa desse simbionte no material analisado, mesmo tendo a glândula salivar (e não o corpo gorduroso/bacteriócitos, sítio clássico de residência de *Sulcia*) como tecido de origem. Esse padrão de "vazamento" transcricional de simbiontes altamente expressos em tecidos adjacentes já foi documentado em outros Hemiptera (ex. *Buchnera* em transcriptomas de afídeo, Bansal et al., 2014). Isso reforça a viabilidade de extrair informação de endossimbiontes a partir de transcriptomas de tecido específico, sem necessidade de sequenciamento metagenômico dedicado.

Diferentemente de uma versão anterior deste texto, a hipótese de vetoração de *Xylella fastidiosa* ou fitoplasma **não permanece em aberto**: o mapeamento genoma-inteiro dos reads brutos contra ambos os genomas de referência (Seção 2.7/3.4, Camada 3) mostrou amplitude de cobertura <0,3% em ambos os casos, com praticamente 100% do sinal residual explicado por cross-mapping de rRNA conservado — um resultado negativo direto, não apenas "ausência de suporte forte". O mesmo padrão de teste dirigido, aplicado à busca viral (varredura por domínio RdRp em todos os contigs, não apenas os pré-selecionados) e à busca por genes de toxina/virulência microbiana em todo o censo de Bacteria+Fungi, não encontrou nenhum candidato que combine (i) identificação como vírus/bactéria/fungo fitopatogênico e (ii) confirmação por múltiplas fontes de evidência independentes. Os quatro vírus confirmados com alta confiança (domínio RdRp + identidade BLASTx) são todos linhagens já descritas como específicas de artrópode, sem precedente de fitopatogenicidade; a busca dirigida pela família RdRp de Phytoreovirus — o grupo clássico de vírus de planta vetorado por Auchenorrhyncha — não teve nenhum hit.

**Inferência concisa sobre a causa do amarelão, restrita ao que os dados sustentam diretamente:** por eliminação sistemática de cada hipótese microbiana testável com os dados disponíveis (vírus, *Xylella*, fitoplasma, fungo fitopatogênico, gene de toxina bacteriana/fúngica), a hipótese que permanece mais bem sustentada é a de efeito direto de um composto salivar do próprio inseto — exatamente a frente já em investigação neste mesmo trabalho (Seção 3.6, 35 candidatos a efetor/toxina secretados). Esta inferência é apresentada com a devida cautela: (i) o desenho de amostra única (1 biblioteca, sem réplicas nem comparação planta sintomática × assintomática) permite apenas testar presença/ausência de cada micro-organismo candidato, nunca causalidade; (ii) um patógeno real, porém raro ou pouco expresso no momento da coleta, pode ter escapado de todos os métodos aplicados; e (iii) a hipótese de efetor salivar em si ainda não foi validada experimentalmente (ver Seção 5). O achado de maior volume nesta camada — 88 hits de *Herbaspirillum* (Seção 3.3), gênero endofítico diazotrófico bem descrito em *Brachiaria*/*Urochloa* — não é um candidato a causador (não há precedente de fitopatogenicidade para o gênero), mas documenta que a biblioteca capturou material bacteriano de origem vegetal via seiva de xilema ingerida, o que reforça (sem confirmar) que outros sinais bacterianos de baixa abundância, se presentes, teriam chance real de detecção neste tipo de amostra.

A confirmação independente por Whokaryote+Tiara (Seção 3.4) reforça a robustez da chamada de endossimbionte nos 3 candidatos com cobertura suficiente para avaliação, mas a limitação de tamanho mínimo de contig (≥5.000 pb) impede o mesmo teste para a maioria dos hits.

Quanto à hipótese de toxina/efetor salivar, a execução completa do secretoma (TMbed) e da priorização (Seções 2.5–2.6) reduziu o conjunto de candidatos plausíveis de dezenas de famílias anotadas para **35 proteínas** que são simultaneamente secretadas e portadoras de um termo/domínio associado a fitotoxicidade em outros Hemiptera — incluindo uma proteína salivar secretada de alta expressão, uma protease tipo veneno com melhor hit em outra cigarrinha (*Macrosteles quadrilineatus*), e uma carboxipeptidase de serina tipo veneno. A anotação dbCAN dedicada (Seção 2.8) encontrou pela primeira vez hits GH28/GH5 (15 proteínas) que a anotação eggNOG original não detectava, mas nenhum desses hits está no secretoma clássico — o que não descarta a hipótese de degradação de parede celular como mecanismo de fitotoxemia, mas indica que, se real, ela não opera pela via clássica de secreção Sec/SPI capturada pelo TMbed (ex. secreção não-clássica, ou celulases/pectinases intracelulares/estruturais). A convergência entre esta lista priorizada e a proteômica já publicada/em andamento pelo grupo UFV (Monteiro, 2019; Rinaldi, 2021, 2026) permanece o teste de robustez mais importante a ser feito, agora com uma lista concreta e finita de candidatos em vez de uma anotação funcional bruta.

---

## 5. Limitações

1. **Desenho de amostra única**: 1 biblioteca de RNA-seq, sem réplicas nem comparação entre plantas sintomáticas e assintomáticas. Toda a Camada 3 (busca por patógeno) permite apenas testar presença/ausência de cada candidato, nunca causalidade ou associação estatística com a severidade do amarelão — confirmação real exigiria PCR/qPCR dirigido em múltiplos indivíduos/plantas, fora do escopo computacional deste trabalho.
2. Cobertura de anotação por eggNOG/KEGG (~43-44%) permanece parcial; mesmo com a anotação dbCAN dedicada (3,8% de cobertura CAZy, 15 hits GH28/GH5), a ausência de hits em proteínas específicas não distingue com certeza entre ausência real da atividade enzimática e limitação de sensibilidade das ferramentas.
3. Uma única biblioteca/condição de glândula salivar limita inferências sobre variação de expressão de candidatos a efetor entre hospedeiros/estádios; não há, no momento, comparação entre forrageiras resistentes/suscetíveis como em Monteiro (2019).
4. *Xylella*/fitoplasma foram testados diretamente por mapeamento genoma-inteiro dos reads brutos e refutados (Seção 3.4); um patógeno real, porém muito divergente do banco de referência usado ou pouco expresso no momento da coleta, ainda poderia escapar dessa triagem.
5. A confirmação estrutural independente de endossimbiontes (Whokaryote+Tiara, Camada 2) só pôde ser aplicada a 3 dos 60 candidatos por causa do corte mínimo de 5.000 pb da ferramenta — a maioria dos genes bacterianos únicos ocorre em transcritos Trinity mais curtos que isso. A validação filogenética adicional (GroEL, Camada 3) não atingiu o critério de suporte estatístico definido (Seção 3.4).
6. A lista de 35 candidatos a efetor/toxina depende inteiramente da regra de secreção clássica (peptídeo sinal Sec/SPI + ≤1 segmento TM, via TMbed); vias de secreção não-clássicas (ex. exossomos, secreção não-canônica) não são capturadas por esse critério e podem excluir candidatos reais, incluindo os 15 hits GH28/GH5 do dbCAN dedicado.
7. A busca por genes de toxina/virulência microbiana (Camada 3) foi baseada em palavras-chave nas anotações funcionais existentes (DIAMOND/eggNOG/Pfam), não em um banco dedicado de toxinas caracterizadas experimentalmente; genes de toxina divergentes ou mal anotados podem ter sido perdidos.
8. Uma quarta camada de triagem taxonômica por contig (CAT/BAT, sem o corte de tamanho mínimo do Whokaryote) foi desenhada mas não executada — o banco de dados necessário (91,6 GB GTDB / 197,5 GB NCBI nr, tamanho real confirmado) foi considerado desproporcional ao ganho esperado frente ao espaço em disco compartilhado do servidor; fica registrado como opção de trabalho futuro.

---

## 6. Status das Análises / Próximas Etapas

Tabela viva, atualizada a cada módulo concluído:

| Módulo | Status | Data | Observação |
|---|---|---|---|
| 1. Montagem + avaliação (Trinity/CD-HIT/TransDecoder/BUSCO) | ✅ Concluído | (histórico) | Seção 3.1 |
| 2. Anotação funcional (DIAMOND/eggNOG/Pfam) + correção de bug de merge | ✅ Concluído | 2026-07-02 | Bug de merge corrigido e validado (`03_annotation/07_fix_annotation_merge.py`); Seção 3.2 |
| 3. Quantificação de expressão (Salmon) | ✅ Concluído | (histórico) | Usado nos módulos 5-7 |
| 4. Triagem de endossimbiontes — Camada 1 (DIAMOND/lineage) | ✅ Concluído | 2026-07-02 | 57 *Sulcia* + 1 *Sodalis*-like; Seção 3.4 |
| 5. Triagem de endossimbiontes — Camada 2 (Whokaryote/Tiara) | ✅ Concluído | 2026-07-23 | 3 concordantes / 0 discordantes / 57 não avaliados (corte de 5.000 pb); Seção 3.4 |
| 6. Predição de secretoma (TMbed, substitui SignalP6/TMHMM) | ✅ Concluído | 2026-07-23 | 1.171 proteínas (9,4%) no secretoma clássico; Seção 3.5 |
| 7. Priorização de efetores/toxinas | ✅ Concluído | 2026-07-23 | 35 candidatos; Seção 3.6 |
| 8. dbCAN dedicado (CAZy GH28/GH5) | ✅ Concluído | 2026-07-23 | 468 proteínas com chamada CAZy, 15 GH28/GH5; Seção 3.2 |
| 9. Censo completo de microbioma (Bacteria 540 + Fungi 256 hits, todos por gênero) | ✅ Concluído | 2026-07-25 | Não apenas os candidatos pré-selecionados; Seção 3.3 |
| 10. Descoberta viral dirigida por domínio RdRp (31 famílias Pfam + DIAMOND vs RefSeq viral) | ✅ Concluído | 2026-07-25 | 4 vírus confirmados por 2 fontes, todos específicos de artrópode; nenhum hit a Phytoreovirus; Seção 3.3 |
| 11. Confirmação/refutação Xylella/fitoplasma por mapeamento genoma-inteiro | ✅ Concluído | 2026-07-25 | Ambos REFUTADOS (breadth <0,3%, 98-100% cross-mapping de rRNA); Seção 3.4 |
| 12. Busca por genes de toxina/virulência microbiana (palavra-chave, Bacteria+Fungi) | ✅ Concluído | 2026-07-25 | Nenhum gene de fitotoxina clássica encontrado; Seção 3.3 |
| 13. Validação filogenética adicional de endossimbionte (GroEL, ML+bootstrap) | ✅ Concluído, resultado inconclusivo | 2026-07-25 | Bootstrap 49-72%, abaixo do critério de 95%; Seção 3.4 |
| 14. CAT/BAT sem corte de tamanho mínimo (Camada 4) | ⏸️ Adiado | — | Banco de dados real confirmado em 91,6-197,5 GB, desproporcional; decisão do usuário |
| 15. Confirmação direcionada Xylella/fitoplasma (PCR) | ✅ Substituído | 2026-07-25 | Mapeamento genoma-inteiro (item 11) cumpriu o mesmo papel sem necessidade de bancada, com resultado negativo |
| 16. Validação experimental dos 35 candidatos a efetor (proteômica/RNAi/ensaio de fitotoxicidade) | 💡 Sugerido, próxima etapa natural | — | Decisão do grupo/laboratório; comparar com Monteiro (2019)/Rinaldi (2021, 2026); reforçado como hipótese mais provável por eliminação (Seção 4) |
| 17. Auditoria de integridade completa (veracidade numérica vs dados brutos, checksum servidor↔local, revisão de bugs) | ✅ Concluído | 2026-08-30 | Nenhum número fabricado; corrigido bug de contagem GH28/GH5 (16→15, substring "GH5" capturava GH56) e bug de merge que deixava 574 valores não-limpos em `cazy` (`03_annotation/09_merge_cazy.py`) |
| 18. Revisão de código dedicada linha-a-linha (finalização da auditoria do item 17) | ✅ Concluído | 2026-08-31 | Confirma que a correção histórica do bug de merge eggNOG se sustenta; achado 1 bug latente de baixa severidade em `06_effector_prioritization/effector_candidates.py` (regex GH28/GH5 não casava subfamílias com sufixo, ex. `GH5_12`) — corrigido, zero impacto nos 35 candidatos publicados (checksum idêntico após reexecução) |

---

## Referências

Andrews, S. (2010). FastQC: a quality control tool for high throughput sequence data. Babraham Bioinformatics, Babraham Institute, Cambridge, UK. https://www.bioinformatics.babraham.ac.uk/projects/fastqc/

Backus, E.A., Serrano, M.S., Ranger, C.M. (2005). Mechanisms of hopperburn: an overview of insect taxonomy, behavior, and physiology. *Annual Review of Entomology*, 50, 125–151. https://doi.org/10.1146/annurev.ento.49.061802.123310

Bansal, R. et al. (2014). Deep sequencing of the transcriptomes of soybean aphid and associated endosymbionts. *PLOS ONE*, 9(9), e106438. https://doi.org/10.1371/journal.pone.0106438

Bennett, G.M., Moran, N.A. (2013). Small, smaller, smallest: the origins and evolution of ancient dual symbioses in a phloem-feeding insect. *Genome Biology and Evolution*, 5(9), 1675–1688. https://doi.org/10.1093/gbe/evt118

Bernhofer, M., Rost, B. (2022). TMbed: transmembrane proteins predicted through language model embeddings. *BMC Bioinformatics*, 23, 326. https://doi.org/10.1186/s12859-022-04873-x

Buchfink, B., Xie, C., Huson, D.H. (2021). Sensitive protein alignments at tree-of-life scale using DIAMOND. *Nature Methods*, 18, 366–368. https://doi.org/10.1038/s41592-021-01101-x

Cantalapiedra, C.P. et al. (2021). eggNOG-mapper v2: functional annotation, orthology assignments, and domain prediction at the metagenomic scale. *Molecular Biology and Evolution*, 38(12), 5825–5829. https://doi.org/10.1093/molbev/msab293

Chen, S., Zhou, Y., Chen, Y., Gu, J. (2018). fastp: an ultra-fast all-in-one FASTQ preprocessor. *Bioinformatics*, 34(17), i884–i890. https://doi.org/10.1093/bioinformatics/bty560

Cornara, D. et al. (2017). Spittlebugs as vectors of *Xylella fastidiosa* in olive orchards in Italy. *Journal of Pest Science*, 90, 521–530. https://doi.org/10.1007/s10340-016-0793-0

Cornara, D. et al. (2018). EPG combined with micro-CT and video recording reveals new insights on the feeding behavior of *Philaenus spumarius*. *Journal of Pest Science*, 91, 941–951.

Eddy, S.R. (2011). Accelerated profile HMM searches. *PLOS Computational Biology*, 7(10), e1002195. https://doi.org/10.1371/journal.pcbi.1002195

Ewels, P., Magnusson, M., Lundin, S., Käller, M. (2016). MultiQC: summarize analysis results for multiple tools and samples in a single report. *Bioinformatics*, 32(19), 3047–3048. https://doi.org/10.1093/bioinformatics/btw354

Foieri, F., Decker-Franco, C., Marino de Remes Lenicov, A.M., Arneodo, J.D. (2022). First identification of bacterial endosymbionts in three South-American spittlebug pests: *Notozulia entreriana*, *Deois mourei* and *Deois knoblauchii*. *Bulletin of Insectology*.

Fu, L., Niu, B., Zhu, Z., Wu, S., Li, W. (2012). CD-HIT: accelerated for clustering the next-generation sequencing data. *Bioinformatics*, 28(23), 3150–3152. https://doi.org/10.1093/bioinformatics/bts565

Grabherr, M.G. et al. (2011). Full-length transcriptome assembly from RNA-Seq data without a reference genome. *Nature Biotechnology*, 29(7), 644–652. https://doi.org/10.1038/nbt.1883

Haas, B.J. et al. (2013). De novo transcript sequence reconstruction from RNA-seq using the Trinity platform for reference generation and analysis. *Nature Protocols*, 8(8), 1494–1512. https://doi.org/10.1038/nprot.2013.084

Hernandez, C.A. et al. (2022). Spittlebugs (Hemiptera: Cercopidae): integrated pest management on gramineous crops in the Neotropical ecozone. *Frontiers in Sustainable Food Systems*, 6, 891417. https://doi.org/10.3389/fsufs.2022.891417

Hoang, D.T., Chernomor, O., von Haeseler, A., Minh, B.Q., Vinh, L.S. (2018). UFBoot2: improving the ultrafast bootstrap approximation. *Molecular Biology and Evolution*, 35(2), 518–522. https://doi.org/10.1093/molbev/msx281

Karlicki, M., Antonowicz, S., Karnkowska, A. (2022). Tiara: deep learning-based classification system for eukaryotic sequences. *Bioinformatics*, 38(2), 344–350. https://doi.org/10.1093/bioinformatics/btab672

Koga, R., Moran, N.A. (2014). Swapping symbionts in spittlebugs: evolutionary replacement of a reduced genome symbiont. *The ISME Journal*, 8, 1237–1249. https://doi.org/10.1038/ismej.2013.235

Langmead, B., Salzberg, S.L. (2012). Fast gapped-read alignment with Bowtie 2. *Nature Methods*, 9(4), 357–359. https://doi.org/10.1038/nmeth.1923

Manni, M. et al. (2021). BUSCO update: novel and streamlined workflows along with broader and deeper phylogenetic coverage for scoring of eukaryotic, prokaryotic, and viral genomes. *Molecular Biology and Evolution*, 38(10), 4647–4654. https://doi.org/10.1093/molbev/msab199

McCutcheon, J.P., Moran, N.A. (2007). Parallel genomic evolution and metabolic interdependence in an ancient symbiosis. *PNAS*, 104(49), 19392–19397. https://doi.org/10.1073/pnas.0708855104

Mistry, J. et al. (2021). Pfam: the protein families database in 2021. *Nucleic Acids Research*, 49(D1), D412–D419. https://doi.org/10.1093/nar/gkaa913

Monteiro, L.P. (2019). Caracterização molecular da interação das cigarrinhas-das-pastagens (*Mahanarva spectabilis*) com diferentes forrageiras. Dissertação de Mestrado, Universidade Federal de Viçosa.

Patro, R., Duggal, G., Love, M.I., Irizarry, R.A., Kingsford, C. (2017). Salmon provides fast and bias-aware quantification of transcript expression. *Nature Methods*, 14(4), 417–419. https://doi.org/10.1038/nmeth.4197

Rinaldi, A.J. (2021). Análise de componentes moleculares da espuma e da toxina presente na glândula salivar de cigarrinha das pastagens. Dissertação de Mestrado, Universidade Federal de Viçosa.

Pronk, L.J.U., Medema, M.H. (2022). Whokaryote: distinguishing eukaryotic and prokaryotic contigs in metagenomes based on gene structure. *Microbial Genomics*, 8(5), 000823. https://doi.org/10.1099/mgen.0.000823

Rinaldi, A.J. et al. (2026). Molecular and structural characterization of foam proteins from *Mahanarva spectabilis* (Distant, 1909) (Hemiptera: Cercopidae) nymphs reveals adaptive features and potential targets for pest control. *Archives of Insect Biochemistry and Physiology*.

Shen, W., Le, S., Li, Y., Hu, F. (2016). SeqKit: a cross-platform and ultrafast toolkit for FASTA/Q file manipulation. *PLOS ONE*, 11(10), e0163962. https://doi.org/10.1371/journal.pone.0163962

Shen, W., Ren, H. (2021). TaxonKit: a practical and efficient NCBI taxonomy toolkit. *Journal of Genetics and Genomics*, 48(9), 844–850. https://doi.org/10.1016/j.jgg.2021.03.006

Shi, M. et al. (2016). Redefining the invertebrate RNA virosphere. *Nature*, 540, 539–543. https://doi.org/10.1038/nature20167

Sotelo, G., Cardona, C. (2001). [Sintomatologia e biologia de cigarrinhas-das-pastagens]. Apud Hernandez et al. (2022).

Thompson, V., González, R. (2005). [Danos de cigarrinhas em gramíneas forrageiras]. Apud Hernandez et al. (2022).

Valério, J.R. et al. (2001). [Caracterização de sintomas de dano de cigarrinhas-das-pastagens]. Apud Hernandez et al. (2022).

Wong, T.K.F., Ly-Trong, N., Ren, H., Banos, H., Roger, A.J., Susko, E., Bielow, C., De Maio, N., Goldman, N., Hahn, M.W., Huttley, G., Lanfear, R., Minh, B.Q. (2025). IQ-TREE 3: phylogenomic inference software using complex evolutionary models. *bioRxiv*. https://doi.org/10.1101/2025.01.15.633177

Zheng, J., Ge, Q., Yan, Y., Zhang, X., Huang, L., Yin, Y. (2023). dbCAN3: automated carbohydrate-active enzyme and substrate annotation. *Nucleic Acids Research*, 51(W1), W115–W121. https://doi.org/10.1093/nar/gkad328
