# Transcriptoma de novo da glândula salivar de *Mahanarva spectabilis* (Hemiptera: Cercopidae): candidatos a efetores fitotóxicos e endossimbiontes associados à síndrome do "amarelão" em pastagens

**Eulalio Santos¹\*, [Coautores a definir]**

¹Departamento de Biologia Geral / Departamento de Bioquímica e Biologia Molecular, Universidade Federal de Viçosa (UFV), Viçosa, MG 36570-900, Brasil

\*Correspondência: eulalio.santos@ufv.br

> **Nota:** este documento é atualizado incrementalmente à medida que os módulos de análise avançam (ver [Seção 6 — Status das Análises](#6-status-das-análises--próximas-etapas) para o estado atual). Última atualização: 2026-07-02.

---

## Resumo / Abstract

*Mahanarva spectabilis* (cigarrinha-das-pastagens, Hemiptera: Cercopidae) é uma das principais pragas de pastagens de *Brachiaria*/*Urochloa* no Brasil, causando o sintoma conhecido como "amarelão": clorose progressiva e secamento foliar ao redor dos pontos de alimentação, com forte impacto na capacidade de suporte de pastagens. Apesar da relevância econômica, nenhum estudo até o momento identificou quimicamente o(s) composto(s) responsável(is) pela fitotoxemia, e a contribuição de microrganismos associados ao inseto (endossimbiontes obrigatórios, possíveis patógenos vetorados) permanece pouco explorada nesta espécie. Aqui apresentamos a montagem de novo e anotação funcional completa do transcriptoma da glândula salivar de *M. spectabilis* (Trinity: 90.344 genes / 103.560 transcritos; CD-HIT-EST 95%; TransDecoder: 12.445 proteínas; BUSCO insecta_odb10: C:96,2%), e iniciamos uma investigação transcriptômica dirigida a duas hipóteses complementares sobre a origem do amarelão: (i) toxinas/efetores salivares fitotóxicos secretados durante a alimentação xilemática, e (ii) contribuição de microrganismos associados à glândula/hospedeiro. A triagem taxonômica das anotações já revelou **57 proteínas com alta identidade (~99%) a *Candidatus* Karelsulcia muelleri e 1 proteína a um simbionte *Sodalis*-like de *Philaenus spumarius***, consistente com o padrão de endossimbiose dupla obrigatória descrito para cigarrinhas-das-pastagens sul-americanas próximas. A anotação funcional já identifica múltiplos candidatos plausíveis a efetor salivar (proteases tipo veneno, peptídeos salivares secretados, mucinas, fosfolipases, domínios EF-hand/Ca-binding, lacase), cuja priorização sistemática (predição de secretoma + expressão + cruzamento com literatura proteômica do mesmo grupo) está em andamento. Este trabalho fornece o primeiro recurso transcriptômico de larga escala para a glândula salivar de *M. spectabilis* e um arcabouço analítico replicável para testar hipóteses sobre fitotoxemia e simbiose em Cercopidae.

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

Reads foram processados com FastQC + fastp (Q≥20, comprimento mínimo 50 bp) e montados de novo com Trinity (`--SS_lib_type RF`, `--min_kmer_cov 2`, `--jaccard_clip`). Transcritos redundantes foram agrupados com CD-HIT-EST (identidade 0,95). ORFs foram preditas com TransDecoder (`--single_best_only`). A completude da montagem foi avaliada com BUSCO (linhagem `insecta_odb10`, 1.367 genes ortólogos de cópia única) e estatísticas gerais com TrinityStats.pl/seqkit.

### 2.3 Anotação funcional

Proteínas preditas foram anotadas por: (i) DIAMOND BLASTp contra o NCBI NR (`--evalue 1e-5 --max-target-seqs 1`); (ii) classificação taxonômica dos melhores hits via TaxonKit (lineage completo, não a versão reformatada por ranks, para evitar perda de classificação — ver Seção 5, Problemas Conhecidos); (iii) eggNOG-mapper (GO, KEGG, COG, CAZy); (iv) HMMER/Pfam-A (domínios proteicos). Todas as fontes foram integradas em uma tabela única (`results/annotation_complete.tsv`, `03_annotation/auto_annotate.py`).

### 2.4 Quantificação de expressão

A abundância de transcritos foi quantificada com Salmon (`expression/salmon-quant.sf`, TPM por transcrito), usada como camada de evidência adicional na priorização de candidatos a efetor (Seção 2.6) e na extração de candidatos a endossimbionte (Seção 2.7).

### 2.5 Predição de secretoma clássico

Proteínas preditas foram/serão submetidas a predição de peptídeo sinal (SignalP 6.0, com fallback para 5.0) e contagem de hélices transmembrana (TMHMM), classificando como "secretoma clássico" as proteínas com peptídeo sinal presente E ≤1 hélice TM (`05_secretome/secretome_predict.py`, 9 fases). **Status: implementado, execução pendente** (depende de instalação de SignalP6/TMHMM em servidor com licença acadêmica — ver Seção 6).

### 2.6 Priorização de candidatos a efetor/toxina salivar

Uma vez disponível o secretoma clássico, os candidatos serão filtrados por: (i) status de secretado; (ii) presença de termos/domínios funcionais associados a fitotoxicidade em Hemiptera na literatura (proteases tipo veneno, peptídeos salivares secretados, mucinas, lacases, fosfolipases A2/B, domínios EF-hand/Ca-binding, CAZymes GH28/GH5 via dbCAN dedicado); e (iii) nível de expressão (TPM). Peso adicional será atribuído a candidatos que se sobrepõem a famílias/proteínas já reportadas na proteômica do mesmo grupo (Monteiro, 2019; Rinaldi, 2021, 2026). **Status: planejado, aguardando secretoma** (`06_effector_prioritization/`).

### 2.7 Triagem de endossimbiontes e microrganismos associados

Na ausência de FASTQ bruto disponível para triagem metagenômica clássica (Kraken2/Kaiju), a triagem foi conduzida em duas camadas: **Camada 1** (implementada) — reaproveitamento das classificações taxonômicas DIAMOND/lineage já geradas na anotação funcional (`07_metagenomic_screen/01_taxonomic_summary.py`), extraindo proteínas com hit em *Sulcia*/*Zinderia*/*Sodalis*-like e sinalizando separadamente hits de baixa prioridade (*Xylella*, fitoplasma) com justificativa biológica explícita (fitoplasmas são floema-limitados; a cigarrinha é xilema-alimentadora). **Camada 2** (planejada, servidor) — confirmação independente via classificação de contigs montados por estrutura gênica (Whokaryote/Tiara) e/ou LCA taxonômico (CAT/BAT), robusta para organismos pouco representados em bancos de referência.

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

### 3.2 Anotação funcional

Da tabela integrada (`results/annotation_complete.tsv`, 12.445 proteínas), 62,1% possuem domínio Pfam, 44,0% possuem termo GO e 42,6% possuem ortólogo KEGG (eggNOG-mapper). Uma coluna CAZy foi adicionada (1,4% das proteínas, 175 no total), mas **nenhum hit às famílias GH28/GH5** (celulases/pectinases classicamente associadas a efetores fitotóxicos de degradação de parede celular) foi encontrado, resultado que reflete a baixa sensibilidade já conhecida da anotação CAZy do eggNOG e motiva uma análise dbCAN dedicada (Seção 2.6).

[[FIG:annotation_summary]]

A distribuição dos 20 termos GO mais frequentes (profundidade ≥ 3) reforça o perfil esperado de um tecido secretor metabolicamente ativo: entre os processos biológicos mais representados estão regulação de processo celular (25,6%) e processo metabólico primário (24,1%); entre as funções moleculares, ligação a composto heterocíclico (11,0%) e ligação a enzima (9,2%); entre os componentes celulares, organela intracelular (33,0%) e organela limitada por membrana (29,9%).

[[FIG:go_distribution]]

Entre os 12.445 proteínas com ortólogo KEGG atribuído, a via mais representada é "Metabolic pathways" (845 proteínas, 6,8%), seguida por "Biosynthesis of secondary metabolites" (388; 3,1%) e "Ribosome" (261; 2,1%). A predominância de vias metabólicas centrais e de categorias amplamente conservadas (Human Diseases, Other) nas posições intermediárias do ranking é esperada para eggNOG-mapper, cuja anotação usa como referência ortólogos humanos/modelo, e não indica especialização funcional exclusiva da glândula salivar.

[[FIG:kegg_pathways_bar]]

[[FIG:kegg_pathways_bubble]]

### 3.3 Distribuição taxonômica dos melhores hits

| Origem taxonômica | N proteínas | % |
|---|---|---|
| Eukaryota | 8.711 | 70,0% |
| Bacteria | 540 | 4,3% |
| Fungi | 256 | 2,1% |
| Viruses | 30 | 0,2% |
| Não classificado | 3.164 | 25,4% |

*Nota: as categorias Eukaryota/Fungi não são mutuamente exclusivas (uma proteína fúngica é, por definição, também eucariótica); a soma das categorias pode exceder 100%.* Entre os hits fúngicos, predominam espécies de *Metarhizium* (fungo entomopatogênico), biologicamente plausível como infecção natural do inseto.

### 3.4 Candidatos a endossimbionte

A extração dirigida de hits com correspondência a simbiontes conhecidos de Auchenorrhyncha identificou **57 proteínas com ~99% de identidade a *Candidatus* Karelsulcia muelleri**, incluindo genes housekeeping clássicos de simbiontes nutricionais (6-fosfofrutoquinase, GAPDH, chaperonina GroEL, enzima málica, fator de iniciação da tradução IF-2) — um padrão de expressão consistente com um simbionte metabolicamente ativo e não com contaminação aleatória. Foi identificada também **1 proteína com hit em simbionte *Sodalis*-like de *Philaenus spumarius*** (cigarrinha-das-pastagens europeia, mesma superfamília Cercopoidea). Esses achados são fortemente consistentes com o padrão de endossimbiose dupla obrigatória (*Sulcia* + *Zinderia*/*Sodalis*-like) já descrito para cigarrinhas-espumantes, incluindo três espécies sul-americanas próximas confirmadas por Foieri et al. (2022).

Dois hits de baixa confiança foram sinalizados separadamente: 1 proteína com 45,1% de identidade a *Xylella fastidiosa* (domínio genérico Bro-N, baixa especificidade) e 1 proteína com 70,0% de identidade a uma DNA polimerase parcial de fitoplasma "aster yellows". Ambos são tratados como ruído exploratório e não como evidência de vetoração — o hit de fitoplasma é biologicamente improvável dado o hábito xilema-alimentador da espécie (ver Seção 1).

### 3.5 Candidatos preliminares a efetor/toxina salivar (pré-secretoma)

Mesmo antes da filtragem formal por secretoma (Seção 2.6), a anotação funcional já revela múltiplas famílias de interesse compatíveis com efetores salivares fitotóxicos descritos em outros Hemiptera: proteases tipo veneno (protease-like, dipeptidil peptidase 4, carboxipeptidase de serina, 5′-nucleotidase tipo veneno de serpente), peptídeos/proteínas salivares secretados (domínio MBF2), óxido nítrico sintase salivar, lacase 1, mucinas (mucin-2/5AC/7/17, hemocitina), fosfolipases A2/B, e 78 domínios EF-hand (ligação a Ca²⁺). A ausência de anotação CAZy sensível (Seção 3.2) deixa em aberto a questão de celulases/pectinases, a ser resolvida com dbCAN dedicado. A priorização quantitativa (peso por secreção, expressão e literatura) está pendente (Seção 2.6).

---

## 4. Discussão

Os resultados de montagem e anotação situam este transcriptoma como um recurso robusto e comparável a outros esforços de sequenciamento de novo em Hemiptera não-modelo (BUSCO >95%, ampla cobertura de anotação funcional). O achado mais imediatamente conclusivo é a confirmação, em nível de transcrito, da endossimbiose dupla obrigatória esperada para Cercopoidea. Os 57 hits de *Sulcia* com identidade ~99% em genes de biossíntese/metabolismo central deixam pouca dúvida quanto à presença ativa desse simbionte no material analisado, mesmo tendo a glândula salivar (e não o corpo gorduroso/bacteriócitos, sítio clássico de residência de *Sulcia*) como tecido de origem. Esse padrão de "vazamento" transcricional de simbiontes altamente expressos em tecidos adjacentes já foi documentado em outros Hemiptera (ex. *Buchnera* em transcriptomas de afídeo, Bansal et al., 2014). Isso reforça a viabilidade de extrair informação de endossimbiontes a partir de transcriptomas de tecido específico, sem necessidade de sequenciamento metagenômico dedicado.

A ausência de suporte forte para *Xylella fastidiosa* ou fitoplasma (hits únicos, fracos ou biologicamente implausíveis) não permite ainda descartar ou confirmar a hipótese de vetoração de patógenos; indica apenas que, se presente, a carga desses organismos no material sequenciado é muito baixa ou ausente. Dado que cigarrinhas-espumantes europeias já são vetores confirmados de *Xylella* (Cornara et al., 2017) e que o hábito xilema-alimentador de *M. spectabilis* é mecanisticamente compatível, esta permanece uma hipótese em aberto que merece confirmação direcionada (PCR específico, por exemplo), não descartável apenas pela ausência de sinal transcriptômico forte em uma única biblioteca.

Quanto à hipótese de toxina/efetor salivar, a anotação já disponível aponta para diversos candidatos promissores, mas a conclusão substantiva sobre quais desses transcritos são efetivamente secretados, abundantes e específicos da glândula salivar depende da execução do módulo de secretoma e da priorização quantitativa (Seção 2.5–2.6), ainda pendentes. A convergência entre esta abordagem transcriptômica e a proteômica já publicada/em andamento pelo grupo UFV (Monteiro, 2019; Rinaldi, 2021, 2026) será um teste importante de robustez para qualquer candidato priorizado.

---

## 5. Limitações

1. Ausência de FASTQ bruto no repositório impede triagem metagenômica clássica (Kraken2/Kaiju) diretamente sobre as reads; a triagem atual depende de contigs/proteínas já montados e de sua representação em bancos de referência.
2. Cobertura de anotação por eggNOG/KEGG (~43-44%) e a ausência de hits CAZy GH28/GH5 podem refletir tanto ausência real dessas atividades enzimáticas quanto limitações de sensibilidade das ferramentas usadas; as duas explicações não são equivalentes.
3. Uma única biblioteca/condição de glândula salivar limita inferências sobre variação de expressão de candidatos a efetor entre hospedeiros/estádios; não há, no momento, comparação entre forrageiras resistentes/suscetíveis como em Monteiro (2019).
4. Os hits de *Xylella*/fitoplasma são de baixa confiança e não substituem confirmação molecular direcionada (PCR/sequenciamento de amplicon).

---

## 6. Status das Análises / Próximas Etapas

Tabela viva, atualizada a cada módulo concluído (ver plano completo em `C:\Users\eulal\.claude\plans\fa-a-um-diagn-stico-desse-crystalline-noodle.md`):

| Módulo | Status | Data | Observação |
|---|---|---|---|
| 1. Montagem + avaliação (Trinity/CD-HIT/TransDecoder/BUSCO) | ✅ Concluído | (histórico) | Seção 3.1 |
| 2. Anotação funcional (DIAMOND/eggNOG/Pfam) + correção de bug de merge | ✅ Concluído | 2026-07-02 | Bug de merge corrigido e validado (`03_annotation/07_fix_annotation_merge.py`); Seção 3.2 |
| 3. Quantificação de expressão (Salmon) | ✅ Concluído | (histórico) | Usado nos módulos 5 e 6 |
| 4. Triagem de endossimbiontes — Camada 1 (DIAMOND/lineage) | ✅ Concluído | 2026-07-02 | 57 Sulcia + 1 Sodalis-like; Seção 3.4 |
| 5. Triagem de endossimbiontes — Camada 2 (Whokaryote/Tiara/CAT-BAT) | ⏳ Pendente | — | Requer servidor; aguardando autorização |
| 6. Predição de secretoma (SignalP6/TMHMM) | ⏳ Pendente | — | Requer servidor + licença SignalP6; script pronto (`05_secretome/secretome_predict.py`) |
| 7. Priorização de efetores/toxinas | ⏳ Pendente | — | Depende do módulo 6; script a implementar (`06_effector_prioritization/`) |
| 8. dbCAN dedicado (CAZy GH28/GH5) | ⏳ Pendente (opcional) | — | Requer servidor |
| 9. Confirmação direcionada Xylella/fitoplasma (PCR) | 💡 Sugerido, fora do escopo computacional | — | Decisão do grupo/laboratório |

---

## Referências

Backus, E.A., Serrano, M.S., Ranger, C.M. (2005). Mechanisms of hopperburn: an overview of insect taxonomy, behavior, and physiology. *Annual Review of Entomology*, 50, 125–151. https://doi.org/10.1146/annurev.ento.49.061802.123310

Bansal, R. et al. (2014). Deep sequencing of the transcriptomes of soybean aphid and associated endosymbionts. *PLOS ONE*, 9(9), e106438. https://doi.org/10.1371/journal.pone.0106438

Bennett, G.M., Moran, N.A. (2013). Small, smaller, smallest: the origins and evolution of ancient dual symbioses in a phloem-feeding insect. *Genome Biology and Evolution*, 5(9), 1675–1688. https://doi.org/10.1093/gbe/evt118

Buchfink, B., Xie, C., Huson, D.H. (2021). Sensitive protein alignments at tree-of-life scale using DIAMOND. *Nature Methods*, 18, 366–368. https://doi.org/10.1038/s41592-021-01101-x

Cantalapiedra, C.P. et al. (2021). eggNOG-mapper v2: functional annotation, orthology assignments, and domain prediction at the metagenomic scale. *Molecular Biology and Evolution*, 38(12), 5825–5829. https://doi.org/10.1093/molbev/msab293

Cornara, D. et al. (2017). Spittlebugs as vectors of *Xylella fastidiosa* in olive orchards in Italy. *Journal of Pest Science*, 90, 521–530. https://doi.org/10.1007/s10340-016-0793-0

Cornara, D. et al. (2018). EPG combined with micro-CT and video recording reveals new insights on the feeding behavior of *Philaenus spumarius*. *Journal of Pest Science*, 91, 941–951.

Foieri, F., Decker-Franco, C., Marino de Remes Lenicov, A.M., Arneodo, J.D. (2022). First identification of bacterial endosymbionts in three South-American spittlebug pests: *Notozulia entreriana*, *Deois mourei* and *Deois knoblauchii*. *Bulletin of Insectology*.

Grabherr, M.G. et al. (2011). Full-length transcriptome assembly from RNA-Seq data without a reference genome. *Nature Biotechnology*, 29(7), 644–652. https://doi.org/10.1038/nbt.1883

Hernandez, C.A. et al. (2022). Spittlebugs (Hemiptera: Cercopidae): integrated pest management on gramineous crops in the Neotropical ecozone. *Frontiers in Sustainable Food Systems*, 6, 891417. https://doi.org/10.3389/fsufs.2022.891417

Koga, R., Moran, N.A. (2014). Swapping symbionts in spittlebugs: evolutionary replacement of a reduced genome symbiont. *The ISME Journal*, 8, 1237–1249. https://doi.org/10.1038/ismej.2013.235

Manni, M. et al. (2021). BUSCO update: novel and streamlined workflows along with broader and deeper phylogenetic coverage for scoring of eukaryotic, prokaryotic, and viral genomes. *Molecular Biology and Evolution*, 38(10), 4647–4654. https://doi.org/10.1093/molbev/msab199

McCutcheon, J.P., Moran, N.A. (2007). Parallel genomic evolution and metabolic interdependence in an ancient symbiosis. *PNAS*, 104(49), 19392–19397. https://doi.org/10.1073/pnas.0708855104

Mistry, J. et al. (2021). Pfam: the protein families database in 2021. *Nucleic Acids Research*, 49(D1), D412–D419. https://doi.org/10.1093/nar/gkaa913

Monteiro, L.P. (2019). Caracterização molecular da interação das cigarrinhas-das-pastagens (*Mahanarva spectabilis*) com diferentes forrageiras. Dissertação de Mestrado, Universidade Federal de Viçosa.

Rinaldi, A.J. (2021). Análise de componentes moleculares da espuma e da toxina presente na glândula salivar de cigarrinha das pastagens. Dissertação de Mestrado, Universidade Federal de Viçosa.

Rinaldi, A.J. et al. (2026). Molecular and structural characterization of foam proteins from *Mahanarva spectabilis* (Distant, 1909) (Hemiptera: Cercopidae) nymphs reveals adaptive features and potential targets for pest control. *Archives of Insect Biochemistry and Physiology*.

Sotelo, G., Cardona, C. (2001). [Sintomatologia e biologia de cigarrinhas-das-pastagens]. Apud Hernandez et al. (2022).

Thompson, V., González, R. (2005). [Danos de cigarrinhas em gramíneas forrageiras]. Apud Hernandez et al. (2022).

Valério, J.R. et al. (2001). [Caracterização de sintomas de dano de cigarrinhas-das-pastagens]. Apud Hernandez et al. (2022).
