# Relatorio final — Camada 3 metagenomica, busca por patogeno causador do amarelao

**Pergunta:** algum patogeno (virus, fungo ou bacteria) causa ou co-causa o "amarelao" em Mahanarva spectabilis / Brachiaria-Urochloa?

**Resposta honesta: NAO ENCONTRADO. Nenhum candidato passa em confirmacao por multiplas fontes independentes.**

## Tabela de veredito final (todos os candidatos avaliados)

| Candidato | Fonte 1 | Fonte 2 | Fonte 3 | Veredito |
|---|---|---|---|---|
| Xylella fastidiosa | DIAMOND fraco (45,1% id., dominio generico Bro-N) | Kraken2-equivalente: mapeamento genoma-inteiro, breadth=0,28%, profundidade=0,16x | 98,0% das posicoes cobertas = rRNA conservado; 1,97% (150bp, profundidade=1, um unico par de reads) = gene de protease S8 generica (tambem nao-diagnostico, amplamente conservado) | **REFUTADO** |
| Aster Yellows phytoplasma | DIAMOND fraco (70% id., DNA polimerase generica) | Mapeamento genoma-inteiro, breadth=0,17%, profundidade=0,006x | 100% das posicoes cobertas = rRNA conservado (artefato) | **REFUTADO** |
| Virus: DN5315 (Flavi-like/Wuhan flea virus) | Dominio RdRp forte (Flavi_NS5, e=1.3e-33) | BLASTx forte (41,6% id., e=1.75e-219) | - | **CONFIRMADO como virus real, mas especifico de inseto — sem precedente de fitopatogenicidade** |
| Virus: DN9206 (Boolarra virus-like) | Dominio RdRp | BLASTx muito forte (87,6% id., quase genoma completo) | - | **CONFIRMADO como virus real, especifico de inseto — irrelevante para o amarelao** |
| Virus: DN124330 (Drosophila C virus-like) | Dominio RdRp | BLASTx forte (69,8% id.) | - | **CONFIRMADO como virus real, especifico de inseto — irrelevante** |
| Virus: DN242325 (Cypovirus-like) | Dominio RdRp muito forte (3 dominios concordantes) | BLASTx moderado (26,3% id.) | - | **CONFIRMADO como virus real, patogeno DO INSETO (poliedrose), nao de planta** |
| Virus: DN36972 (Grapevine vein clearing virus-like) | Dominio RdRp fraco | BLASTx fraco (26,8% id.) | Sem validacao adicional | **INCONCLUSIVO** — unico lead com "sabor" de virus de planta, mas evidencia fraca demais |
| Virus: DN10734 (isoformas com hits inconsistentes) | Dominio RdRp fraco | BLASTx inconsistente entre isoformas (RT de CaMV, ORFs de virus de inseto diferentes) | - | **NAO CONFIRMAVEL** — provavel dominio promiscuo RT/RdRp, nao especie identificavel |
| Virus: DN6866, DN11520, DN59657 | Dominio RdRp presente | Sem hit BLASTx | - | **INCONCLUSIVO** — podem ser virus reais muito divergentes ou falso-positivo do HMM |
| Fitoreovirus (marcador especifico PF27669/PF27845) | Busca dirigida, nenhum hit em nenhum contig | - | - | **AUSENTE** — hipotese mais direta de "virus vetorado por Auchenorrhyncha causando doenca de planta" sem suporte nos dados atuais |
| Fusarium spp. (murcha vascular, coloniza xilema) | 8 hits DIAMOND, generos fitopatogenicos conhecidos | Sem confirmacao independente (sem Kraken2/mapeamento dedicado) | - | **INCONCLUSIVO** — candidato mais plausivel mecanisticamente (xilema=sintoma do amarelao) mas sinal fraco |
| Erysiphe pulchra (oidio) | 15 hits DIAMOND | Mecanisticamente improvavel (ataca folha, nao xilema) | - | **IMPROVAVEL** |
| Entomophthora muscae + Massospora + Metarhizium (77% dos hits de Fungi) | Dominante | Entomopatogenicos, do proprio inseto | - | **IRRELEVANTE para o amarelao** (mas relevante para biologia/controle do inseto) |
| Sulcia/Karelsulcia (endossimbionte obrigatorio) | GC% Mann-Whitney p=8e-23 | Identidade BLAST 99,4% | Filogenia GroEL INCONCLUSIVA (bootstrap 49-72%, abaixo do criterio de 95%) | **Simbionte confirmado (2 de 3 fontes), mas e mutualista conhecido — NAO e patogeno, e pano de fundo** |

## Limitacoes que permanecem validas para qualquer conclusao

1. **Desenho de amostra unica** (1 biblioteca RNA-seq, sem replicas, sem comparacao planta sintomatica vs. assintomatica) — mesmo que um candidato fosse confirmado, isso seria "presenca", nunca "causa" do amarelao. Confirmacao de causalidade exige PCR/qPCR em multiplos individuos + design experimental comparativo.
2. **CAT/BAT (Bloco 4) foi adiado** — banco de dados real confirmado em 91,6GB (GTDB) a 197,5GB (nr), desproporcional ao ganho estimado. Fica registrado como opcao de trabalho futuro se o usuario decidir alocar esse espaco depois.
3. **Sem confirmacao de que a biblioteca capturaria adequadamente RNA viral/bacteriano** (protocolo de selecao da biblioteca nao documentado em README/metadata no servidor) — ausencia de sinal pode refletir limitacao tecnica, nao ausencia biologica real.
4. Fusarium (candidato mais mecanisticamente plausivel) tem sinal fraco demais (8 hits) para qualquer afirmacao — precisaria de validacao dedicada (Kraken2/mapeamento como foi feito para Xylella/fitoplasma) se o usuario quiser aprofundar.

## Conclusao

A hipotese de um patogeno microbiano (virus/bacteria/fungo) causando o amarelao **nao encontra suporte nos dados de transcriptoma de glandula salivar disponiveis**. Os achados mais robustos desta Camada 3 sao, na verdade, **negativos/refutadores** dos 2 leads que ja existiam (Xylella, fitoplasma), e a descoberta de 4 virus especificos de inseto (irrelevantes para a doenca de planta). Isso reforca, por eliminacao, a hipotese alternativa ja levantada na literatura do proprio grupo (Backus et al. 2005; fitotoxemia por efetor/toxina salival, ja em investigacao via o modulo de priorizacao de efetores deste mesmo projeto) como a explicacao mais provavel para o amarelao — nao um patogeno vetorado.
