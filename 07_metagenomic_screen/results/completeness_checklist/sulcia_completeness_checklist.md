# Checklist informal de completude — candidatos Sulcia/Sodalis (NAO e CheckM2, ver nota)

58 proteinas totais no conjunto candidato (57 Karelsulcia + 1 Sodalis-like), categorizadas por funcao a partir do `diamond_title`:

## Traducao / maquinaria ribossomal (14 genes)
50S ribosomal protein L3, L4, L7/L12, L17; 30S ribosomal protein S7, S10, S12; translation elongation factor Tu; translation initiation factor IF-2; elongation factor G; methionine-tRNA ligase (x2); phenylalanyl-tRNA synthetase alpha subunit; polyribonucleotide nucleotidyltransferase

## Metabolismo central / energia (10 genes)
glyceraldehyde 3-phosphate dehydrogenase; 6-phosphofructokinase; putative NAD(P)-dependent malic enzyme; pyruvate dehydrogenase E1 beta; dihydrolipoamide acyltransferase E2; F0F1 ATP synthase subunit beta; ATP synthase F1 alpha; phosphate acetyltransferase; transketolase + transketolase C-term; cytochrome c oxidase cbb3-type ccoP subunit

## Biossintese de aminoacidos de cadeia ramificada / aromaticos (BCAA - via classica de Sulcia na literatura) (9 genes)
acetolactate synthase large subunit (x2); ketol-acid reductoisomerase; dihydroxy-acid dehydratase; 2-isopropylmalate synthase; 3-isopropylmalate dehydratase (large+small subunit); 3-isopropylmalate dehydrogenase; putative phospho-2-dehydro-3-deoxyheptonate aldolase/chorismate mutase

## Biossintese de outros aminoacidos (arginina/lisina/treonina/homoserina) (11 genes)
argininosuccinate synthase (x2); acetylornithine deacetylase; acetylornithine aminotransferase; acetylglutamate kinase; ornithine carbamoyltransferase; N-acetyl-gamma-glutamyl-phosphate reductase; carbamyl phosphate synthase (large+small); diaminopimelate epimerase; aspartokinase/homoserine dehydrogenase; homoserine kinase; threonine synthase; threonine dehydratase; Glu/Leu/Phe/Val dehydrogenase; putative aspartate kinase

## Chaperonas / choque termico (2 genes)
60 kDa chaperonin GroEL; molecular chaperone DnaK

## Replicacao/reparo de DNA (2 genes)
DNA gyrase subunit A; DNA gyrase subunit B

## Outros / hipoteticos (3 genes)
putative trmH/spoU family tRNA/rRNA methyltransferase; lipoyl synthase; hypothetical protein CE195_09980

---

## Interpretacao

O padrao encontrado (traducao + metabolismo central + biossintese de BCAA fortemente representada) e **exatamente o esperado da literatura** para Sulcia/Karelsulcia (McCutcheon & Moran 2007; Bennett & Moran 2013) — Sulcia e classicamente descrito como o simbionte que supre aminoacidos essenciais (especialmente BCAA e aromaticos) que o inseto e o co-simbionte (Zinderia/Sodalis) nao conseguem sintetizar sozinhos. A presenca de ~9 genes dessa via especifica, sem nenhum gene de via metabolica tipicamente ausente em genomas reduzidos (ex. biossintese de nucleotideos de novo, muitos cofatores), e consistente com o perfil de genoma extremamente reduzido e especializado ja descrito.

**NAO e uma metrica de completude real tipo CheckM2** — CheckM2 avalia completude/contaminacao de um genoma bacteriano MONTADO comparando contra um conjunto de marcadores universais de copia unica; aqui nao existe um MAG, apenas 58 transcritos individuais recuperados de um transcriptoma de hospedeiro. Nao ha como calcular % de completude do genoma total do Sulcia a partir disso (o genoma publicado de Karelsulcia tem ~190kb / poucas centenas de genes; 58 recuperados e uma fracao, mas a fracao exata depende de quantos genes existem no genoma real, que nao foi montado aqui).
