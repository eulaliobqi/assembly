# Roteiro de apresentação — Transcriptoma da glândula salivar de *Mahanarva spectabilis*

> Estudo de caso para minicurso. Bloco curto, ~15-20 minutos (+ 3-4 min de anexo opcional com código). Narração completa, pronta para ler/adaptar. Marcações `[SLIDE]` indicam quando trocar de imagem — usar as figuras em `figures/` (ou as páginas correspondentes do `artigo.docx`).

---

## 0. Abertura — o problema (≈ 2 min)

**[SLIDE: foto de pastagem com sintoma de amarelão, ou título]**

Quem já andou numa pastagem de Brachiaria e viu aquelas manchas amareladas, quase queimadas, ao redor dos pontos onde um inseto se alimentou? Isso tem nome: "amarelão". É causado por uma cigarrinha, a *Mahanarva spectabilis*, e é um dos problemas mais caros da pecuária brasileira — populações de 25 a 50 adultos por metro quadrado já reduzem a capacidade de suporte da pastagem em até um terço.

E aqui está o que torna esse caso interessante para a gente hoje: apesar de décadas de manejo dessa praga, **ninguém nunca identificou quimicamente qual é a toxina** que ela injeta na planta. A gente sabe o efeito, mas não sabe a causa molecular.

Foi essa pergunta que motivou o trabalho que vou apresentar: montar o transcriptoma da glândula salivar dessa cigarrinha — o órgão que produz a saliva injetada na planta — e usar bioinformática pra procurar candidatos a essa toxina, além de investigar uma segunda hipótese: será que microrganismos que vivem dentro do inseto têm algum papel nisso?

---

## 1. Duas hipóteses, um transcriptoma (≈ 1-2 min)

**[SLIDE: esquema simples — inseto, glândula salivar, planta, com duas setas: "toxina salivar?" e "microrganismo?"]**

A gente está testando duas hipóteses ao mesmo tempo, e elas não se excluem:

Primeira: existe uma proteína ou peptídeo secretado pela glândula salivar que é diretamente fitotóxico — que ataca o tecido da planta.

Segunda: cigarrinhas-das-pastagens são classicamente conhecidas por carregar endossimbiontes bacterianos obrigatórios — bactérias que vivem dentro delas há milhões de anos e complementam a dieta pobre em nutrientes do xilema. A pergunta é se esse sistema também aparece aqui, e se há sinal de outros microrganismos, como patógenos de planta.

Pra responder isso, o primeiro passo é: montar o transcriptoma. E é aqui que entra a parte que interessa pra quem está aprendendo o pipeline.

---

## 2. O pipeline, em uma frase (≈ 1 min)

**[SLIDE: fluxograma Trinity → CD-HIT-EST → TransDecoder → BUSCO → anotação]**

RNA da glândula salivar foi sequenciado, montado *de novo* com o Trinity — sem genoma de referência, porque não existe um pra essa espécie —, depois a redundância foi reduzida com CD-HIT-EST, as proteínas foram preditas com TransDecoder, e a qualidade de tudo isso foi avaliada com BUSCO antes de qualquer anotação funcional.

Quatro ferramentas, quatro perguntas diferentes. É exatamente isso que a próxima figura mostra.

---

## 3. Figura 1 — controle de qualidade da montagem (≈ 4-5 min)

**[SLIDE: figures/assembly_qc_summary.png — painel A-D]**

Essa figura resume as quatro métricas que todo mundo usa pra saber se um transcriptoma *de novo* é confiável. Vou passar por cada painel.

**Painel A.** Depois do Trinity e do CD-HIT-EST a 95% de identidade, a gente ficou com 103.560 transcritos não-redundantes, agrupados em 90.344 genes — ou seja, o CD-HIT colapsou quase 13 mil transcritos que eram, na prática, cópias quase idênticas umas das outras. Isso é esperado: o Trinity tende a superestimar isoformas, e sem essa limpeza a gente estaria contando a mesma coisa várias vezes. Desses 103.560 transcritos, só 12.445 tinham uma fase de leitura aberta — uma ORF — longa o suficiente pra virar proteína predita pelo TransDecoder. E isso também é esperado: a maior parte de um transcriptoma são transcritos curtos, RNAs não-codificantes, ou UTRs sem potencial codificante.

**Painel B.** Essa é a curva N50 — provavelmente a métrica mais citada e mais mal-entendida de montagem *de novo*. O que ela significa? Ordena todos os contigs do maior pro menor, vai somando o comprimento, e pergunta: em que tamanho de contig eu acumulei metade de todas as bases montadas? Aqui, esse valor é 738 pares de base. Não existe um "N50 bom" universal — depende do organismo, da profundidade de sequenciamento, da complexidade do transcriptoma —, mas 738 pb está na faixa esperada pra um transcriptoma de inseto não-modelo.

**Painel C.** BUSCO mede completude, não tamanho. A lógica é: existe um conjunto de genes de cópia única que praticamente todo inseto tem — aqui, 1.367 genes do banco `insecta_odb10`. A gente procura esses genes na montagem. O resultado: 96,2% completos. Só que reparem numa coisa interessante — desses 96,2%, mais da metade (56,3%) aparece **duplicado**, não em cópia única. Isso não é um erro. É esperado quando você monta a partir de um tecido só, sem filtrar isoformas alternativas: o mesmo gene aparece várias vezes porque tem várias variantes de splicing. Ou seja, alta completude aqui, mais um lembrete de por que a etapa de CD-HIT do painel A é necessária.

**Painel D.** E dentro das 12.445 proteínas preditas, o TransDecoder classifica cada ORF por tipo: completa — com metionina inicial e stop códon —, ou parcial em uma das pontas, ou interna — sem nenhuma das duas bordas, geralmente porque o transcrito estava fragmentado. Aqui, 58% são completas. É um número saudável; se a maioria fosse "interna", seria sinal de uma montagem mais fragmentada do que essa.

Então, resumindo esse bloco inteiro numa frase: essa montagem é grande, redundância foi tratada, está biologicamente completa e a maior parte das proteínas preditas está inteira. Isso dá segurança pra usar esses dados nas perguntas biológicas que vêm a seguir.

---

## 4. Figura 2 — quem são essas proteínas? (≈ 2-3 min)

**[SLIDE: figures/annotation_summary.png — painel A-B]**

Ter uma proteína predita não significa saber o que ela faz. Pra isso, cruzamos as 12.445 proteínas contra bancos de dados: Pfam pra domínios estruturais, eggNOG-mapper pra GO e KEGG, e DIAMOND contra o NCBI para descobrir a que organismo cada sequência mais se parece.

Painel A: 75% das proteínas tiveram algum hit no DIAMOND, 62% têm domínio Pfam reconhecido, e por volta de 43-44% têm termo GO ou ortólogo KEGG atribuído. Isso é normal — organismo não-modelo, sem genoma de referência, uma fração real do transcriptoma simplesmente não tem homólogo caracterizado em banco nenhum ainda.

Painel B é onde fica interessante: a origem taxonômica desses hits. 70% são de Eukaryota — o esperado, é o próprio inseto. Mas 4,3% batem em Bacteria e 2,1% em Fungi. Uma glândula salivar não devia ter bactéria nem fungo "dentro" dela, a não ser que... tenha, de fato. E é exatamente isso que a próxima parte investiga.

---

## 5. Figuras 3 a 5 — GO e KEGG, rapidamente (≈ 2 min)

**[SLIDE: figures/go_distribution.png, depois figures/kegg_pathways_bar.png e kegg_pathways_bubble.png]**

Não vou me alongar aqui porque essas figuras contam uma história esperada: os termos GO mais frequentes são coisas genéricas de metabolismo e ligação a proteína, os componentes celulares mais citados são organela e membrana. As vias KEGG também: metabolismo central, ribossomo, processamento no retículo. Nada disso é exclusivo de glândula salivar — é o "ruído de fundo" normal de qualquer transcriptoma de tecido metabolicamente ativo. A parte específica do amarelão não está aqui, nesses termos gerais; está nas categorias funcionais específicas que vou mostrar já já.

---

## 6. Os endossimbiontes (≈ 2-3 min)

**[SLIDE: tabela de hits — 57 proteínas Sulcia, 1 proteína Sodalis-like]**

Voltando àqueles 4,3% de hits em bactéria do painel B: quando a gente filtra especificamente por simbiontes conhecidos de cigarrinhas, aparecem **57 proteínas com quase 99% de identidade a *Candidatus* Karelsulcia muelleri** — e não são proteínas quaisquer, são genes de manutenção básica da célula: fosfofrutoquinase, GAPDH, a chaperonina GroEL. Esse é o perfil clássico de um endossimbionte metabolicamente ativo, não de contaminação aleatória de bancada.

Isso bate com a literatura: cigarrinhas-das-pastagens sul-americanas próximas já tiveram esse mesmo simbionte confirmado por 16S rRNA. E encontramos também 1 proteína batendo num simbionte do tipo *Sodalis*, já descrito numa cigarrinha europeia da mesma superfamília. Ou seja: *Sulcia* mais um segundo parceiro — o padrão clássico de endossimbiose dupla dessas cigarrinhas parece estar presente aqui também, e isso é a primeira vez que se documenta isso pra esse gênero.

Vale um comentário metodológico rápido: a gente não tinha FASTQ bruto pra rodar uma triagem metagenômica clássica. Então essa detecção veio de reaproveitar a própria anotação taxonômica que já tínhamos gerado — um atalho que funciona bem quando o simbionte é altamente expresso, mesmo em tecido que não é o clássico "corpo gorduroso" onde ele mora.

E, por transparência: apareceram também 2 hits fracos, um pra *Xylella fastidiosa* e outro pra fitoplasma — mas com baixíssima confiança, e no caso do fitoplasma, biologicamente improvável, porque fitoplasma vive só no floema e essa cigarrinha se alimenta só de xilema. Não estou descartando a hipótese de vetor de patógeno, só dizendo que esse dado sozinho não prova nada — precisaria de PCR direcionado pra confirmar.

---

## 7. E a toxina? Candidatos a efetor salivar (≈ 2 min)

**[SLIDE: lista de famílias — proteases tipo veneno, mucinas, fosfolipases, EF-hand, laccase]**

Voltando à primeira hipótese. Mesmo sem ter rodado ainda a etapa de predição de secretoma — que filtra quais proteínas realmente têm peptídeo sinal e são de fato secretadas —, a anotação já aponta famílias muito sugestivas: proteases do tipo veneno, um peptídeo salivar secretado, óxido nítrico sintase salivar, laccase, várias mucinas, fosfolipases A2 e B, e 78 domínios de ligação a cálcio, os EF-hand.

Por que essas famílias chamam atenção? Porque proteases tipo veneno e fosfolipases já são descritas como efetores fitotóxicos em outros hemípteros, e mucinas em grande quantidade são consistentes com a formação daquela bainha salivar que a cigarrinha constrói ao redor do vaso do xilema enquanto se alimenta.

Isso ainda não é uma resposta — é uma lista de suspeitos. O próximo passo do pipeline, que ainda está pendente, é rodar a predição de secretoma pra filtrar só quem é realmente secretado, cruzar com o nível de expressão, e comparar com achados de proteômica que o mesmo grupo já publicou pra essa espécie.

---

## 8. Onde isso para agora, e por que mostrar isso num minicurso (≈ 1-2 min)

**[SLIDE: tabela de status do artigo.md, Seção 6]**

Esse é o estado real do projeto hoje: montagem, anotação e a primeira camada de triagem de simbionte estão prontas. Predição de secretoma, priorização de efetor e uma segunda camada de confirmação de simbionte — essa via classificação direta dos contigs montados — ainda estão pendentes, esperando processamento em servidor.

E eu queria fechar com o motivo de estar mostrando um projeto inacabado, e não um artigo publicado e redondo: porque isso *é* como bioinformática de verdade acontece. Vocês não vão sair de um transcriptoma direto pra uma resposta. Vão sair com um funil de candidatos, alguns achados sólidos — como esse endossimbionte —, e uma lista clara do que falta rodar. Cada figura que eu mostrei hoje corresponde a uma pergunta que vocês também vão poder fazer nos dados de vocês: minha montagem está completa? Está redundante? O que essas proteínas realmente são? E o que, dentro disso, pode responder à pergunta biológica que me trouxe até aqui?

---

## 9. Anexo — os comandos por trás de cada painel (opcional, ≈ 3-4 min)

**[SLIDE: bloco de código, um por vez, seguindo a ordem da Figura 1]**

> Use este bloco se a turma pedir "mas como isso roda de verdade?", ou se sobrar tempo. Os comandos vêm de `01_quality_assembly/02_trinity_assembly.sh` e `02_assembly_evaluation/03_stats_busco.sh` — os dois scripts do repositório escritos com comentário de rationale em cada parâmetro, pensados originalmente como material de referência. Não são os scripts que geraram os números exatos deste artigo (esses estão em `script-assembly.sh`, sem comentário), mas ensinam o pipeline melhor do que qualquer um dos outros.

Cada bloco de código aqui corresponde a um painel da Figura 1 que a gente já viu.

**Painel A — Trinity + CD-HIT-EST:**

```bash
Trinity \
    --seqType fq \
    --left "${TRIMMED_R1}" --right "${TRIMMED_R2}" \
    --SS_lib_type RF \
    --min_kmer_cov 2 \
    --min_contig_length 300 \
    --jaccard_clip \
    --max_memory 64G --CPU 16 \
    --output "${TRINITY_OUT}"

cd-hit-est \
    -i "${TRINITY_FASTA}" -o "${CDHIT_OUT}" \
    -c 0.95 -n 8 -T 16 -M 0 -d 0
```

Dois pontos pra chamar atenção na hora de explicar: `--SS_lib_type RF` diz ao Trinity que a biblioteca é *strand-specific* — sem isso, ele pode fundir transcritos de fita sentido e antissentido como se fossem um só. E o `-c 0.95` do CD-HIT é exatamente o corte de 95% de identidade que colapsou aqueles 12.857 transcritos redundantes do painel A.

**Painel B — estatísticas e curva N50:**

```bash
TrinityStats.pl "${CDHIT_FASTA}" | tee cdhit_stats.txt
```

Um comando só, mas ele que gera todos os números da curva Nx que a gente comentou — N10, N20... até N50.

**Painel C — BUSCO:**

```bash
busco \
    --input "${CDHIT_FASTA}" \
    --out "busco_mahanarva" \
    --lineage_dataset insecta_odb10 \
    --mode transcriptome \
    --cpu 16 --force
```

Vale ler em voz alta o comentário que está no script original sobre esse painel, porque resume bem a discussão que a gente teve sobre os 56% duplicados:

> "A salivary gland transcriptome is expected to show lower completeness than a whole-body transcriptome... isoforms may inflate duplicated BUSCOs. This is EXPECTED and does NOT indicate a low-quality assembly."

**Painel D — TransDecoder:**

```bash
TransDecoder.LongOrfs -t "${CDHIT_OUT}" -m 100

TransDecoder.Predict -t "${CDHIT_OUT}" --single_best_only
```

`-m 100` é o comprimento mínimo de ORF em aminoácidos — os comentários do script justificam esse valor (em vez do padrão, que é maior) exatamente pela hipótese biológica do projeto: peptídeos secretados pequenos, como um efetor salivar, podem ser descartados por um filtro mais rígido. É um bom exemplo de como um parâmetro de bioinformática não é neutro — ele já embute uma escolha ligada à pergunta científica.

---

## Referência rápida — números usados neste roteiro

| Métrica | Valor |
|---|---|
| Genes / transcritos Trinity (pós CD-HIT-EST 95%) | 90.344 / 103.560 |
| GC | 34,21% |
| N50 | 738 pb |
| Transcritos redundantes colapsados pelo CD-HIT | 12.857 |
| Proteínas TransDecoder (`--single_best_only`) | 12.445 |
| ORFs completas / 5'-parcial / internas / 3'-parcial | 58,4% / 16,3% / 16,0% / 9,4% |
| BUSCO (insecta_odb10, n=1.367) | C:96,2% [S:39,9%, D:56,3%], F:1,9%, M:1,9% |
| Cobertura Pfam / GO / KEGG / DIAMOND | 62,1% / 44,0% / 42,6% / 75,1% |
| Eukaryota / Bacteria / Fungi / Viruses / não classificado | 70,0% / 4,3% / 2,1% / 0,2% / 25,4% |
| Hits *Sulcia* / *Sodalis*-like | 57 / 1 |
| Status pendente | Secretoma, priorização de efetores, Camada 2 de endossimbiontes |
