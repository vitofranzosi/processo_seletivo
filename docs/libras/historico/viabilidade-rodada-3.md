> **Registro histórico.** Esta é a análise de viabilidade da **rodada 3** (versão 3 do catálogo, 316
> identificadores), preservada sem alterações de conteúdo. A revisão que se seguiu mostrou que algumas conclusões
> excediam as métricas; a vigente é [`../viabilidade.md`](../viabilidade.md). Os links apontam para o estado atual.

# Viabilidade da hipótese: recorrência e reuso em Libras

**Medição de 2026-10-11 — versão 3 do catálogo (rodada 3).** Baseada nos três editais **simulados** do
corpus, em dois editais **reais** do Cefor (28/2026 e 59/2026) inventariados por inteiro, na sondagem em 18
editais reais e no protótipo da camada comunicativa. As análises anteriores estão preservadas:
[rodada 1](viabilidade-rodada-1.md) e [rodada 2](viabilidade-rodada-2.md).

> **O que mudou desde a rodada 2.** Entraram dois editais reais, com os anexos que estão dentro do PDF: 207 e
> 107 linhas de cobertura, 162 unidades novas, seis narrativas. O método não mudou. Três coisas mudaram na
> resposta: **(1)** a hipótese da rodada 1 — o texto que o sistema escreve sozinho é o candidato natural a
> reuso — **não se confirma** no texto real, que diz as mesmas coisas com outras palavras; **(2)** a
> recorrência que a sondagem sugeria **se confirma** no inventário, entre os dois editais reais; **(3)** o
> Cefor **já publica** o edital em Libras (o 28/2026 tem vídeo de 75 minutos), o que muda o experimento
> possível.

## A decisão em uma frase

**Há base para um experimento com profissionais de Libras e participantes surdos, agora com material real e
com uma tradução institucional para comparar; continua não havendo base para desenvolver uma biblioteca
audiovisual integrada ao sistema.** Nos editais reais, só 0% e 1% das palavras têm texto idêntico ao que o
sistema escreve; entre os dois editais reais, 12% e 30% (15% e 40% sem contar caixa e pontuação). A
recorrência que existe é a do **texto da casa**, que o Cefor copia de um edital para o seguinte — e que o
sistema hoje não identifica, porque é redação livre. O ganho mais provável, a verificar, continua sendo o de
**roteiros e soluções tradutórias**; o de **gravações** é o mais incerto, e só é discutível no texto da casa.

---

## 1. A amostra, e o que ela não permite dizer

| | Simulados | Reais | Sondagem complementar |
|---|---|---|---|
| O quê | 91/2026, 92/2026, 01/2026, publicados pelo sistema, e 4 Retificações | 28/2026 e 59/2026 do Cefor, versão consolidada | 18 editais reais do Cefor, 2024–2026 |
| Natureza | texto livre redigido pela auditoria do PDF e pelo `seed_demo` | **documento oficial**, escrito fora do sistema, com seus defeitos | reais, fora do repositório |
| Tipos de certame | ingresso em curso (91), bolsistas (92), contratação (01) | ingresso em curso: pós-graduação EaD (28) e FIC presencial de Libras (59) | vários |
| Inventário | integral, com unidade por linha e narrativas | integral, inclusive anexos, com narrativas | nenhum: comparação automática de frases |
| Versões | original e Retificações, por diferença | **só a consolidada**: os atos não foram lidos | — |
| Serve para | medir o que o sistema escreve sozinho | medir se o texto do sistema reaparece no real, e se o texto real se repete | estimar a recorrência entre muitos editais reais |
| Não serve para | medir recorrência de texto livre | medir o efeito de uma Retificação; generalizar para outras Unidades | equivalência de sentido |

**Fato.** O 91/2026 simulado foi calibrado no 28/2026 pela auditoria do PDF de 08/10 (cenário A). O par
91 × 28 é, portanto, a comparação mais favorável possível entre texto do sistema e texto real.

**Dois editais reais é pouco**, de uma Unidade só, os dois de ingresso em curso. A recorrência entre eles
pode ser maior do que entre editais de setores diferentes, e menor do que entre dois anos do mesmo curso.

## 2. Métricas

Reproduzíveis com `python3 docs/libras/ferramentas/medir.py` ([`ferramentas/`](../ferramentas/README.md)).

### 2.1 Unidades e ocorrências

| Medida | Versão 1 | Versão 2 | **Versão 3** |
|---|---|---|---|
| Identificadores | 126 | 154 (142 ativos) | **316** (304 ativos, 12 desdobrados) |
| Ocorrências (sem rodapé) | 374 | 377 | **699** |
| Unidades novas por edital (91 · 92 · 01 · 28 · 59) | 72 · 49 · 4 | 72 · 62 · 7 | **72 · 62 · 7 · 141 · 21** |
| Unidades em 1 · 2 · 3 · 4 · 5 editais | 69 · 31 · 24 | 92 · 26 · 22 | **180 · 76 · 28 · 10 · 8** |

**O 28/2026 trouxe 141 unidades novas; o 59/2026, 21.** Processado depois do 28, o 59 encontrou no catálogo 79
das suas 100 unidades. Vinte e uma unidades anteriores, nascidas nos simulados, mudaram de classificação ao
ganhar ocorrência real com outra redação (`EXATA` ou `INÉDITA` → `SEMELHANTE`, ou → `PARAMETRIZÁVEL`).

### 2.2 Palavras: simulados entre si

| Edital | Palavras | Unidade recorre em outro simulado | Texto idêntico em outro simulado |
|---|---|---|---|
| 91/2026 | 1.436 | 61% | 11% |
| 92/2026 | 3.711 | 63% | 5% |
| 01/2026 | 654 | 86% | 17% |
| **Simulados** | **5.801** | **65%** | **8%** |

Iguais aos da versão 2: a entrada dos reais não altera a medida entre os simulados.

### 2.3 Palavras: editais reais

| Edital | Palavras | Recorre em simulado | **Idêntico a simulado** | Recorre no outro real | **Idêntico ao outro real** | Quase idêntico ao outro real |
|---|---|---|---|---|---|---|
| 28/2026 | 8.611 | 17% | **0%** | 32% | **12%** | 15% |
| 59/2026 | 3.357 | 25% | **1%** | 77% | **30%** | 40% |

*Recorre*: a mesma unidade (função) aparece no outro grupo. *Idêntico*: a linha tem o mesmo texto, sem contar a
numeração. *Quase idêntico*: também sem contar caixa e pontuação (“Edital” × “edital”; “;” × “.”). Nenhuma das
três mede tradução reutilizável.

**Fato.** O texto que o sistema escreve não reaparece nos editais reais — nem no 28/2026, em que a simulação foi
calibrada. A mesma regra (o sorteio, a reversão, a concorrência simultânea, a convocação de suplentes) está nos
dois, e as palavras são outras: o sistema gera a frase a partir da regra; o Cefor escreve mais, e outras coisas
(o software e a semente do sorteio, o universo dos habilitados, a substituição do indeferido).

**Fato.** Entre os dois editais reais, a recorrência é de outra ordem: 77% das palavras do 59/2026 estão em
unidades que o 28/2026 também tem, e 30% em linhas de texto idêntico.

### 2.4 Texto idêntico entre os dois reais, por família

| Família | Unidades nos dois | Com texto idêntico | Palavras do 59/2026 com texto idêntico ao 28/2026 |
|---|---|---|---|
| ANX — anexos | 4 | 2 | 233 de 255 (o Requerimento de Matrícula e a sua declaração) |
| GER — disposições gerais | 9 | 8 | 219 de 483 |
| CLA — classificação | 8 | 4 | 148 de 465 |
| CON — matrícula | 7 | 4 | 147 de 290 |
| OFE — oferta e certificado | 5 | 2 | 75 de 543 |
| REC — recurso | 7 | 5 | 74 de 137 |
| INS — inscrição | 10 | 2 | 72 de 400 |
| ATO — abertura e fecho | 6 | 3 | 53 de 194 |
| DOC, CRO, REQ, PER | 6, 12, 2, 1 | 0 | 0 |

**DOC tem 0% de texto idêntico e é, ao mesmo tempo, das famílias mais parecidas**: a lista de identidades e o
documento militar diferem só no ponto final (`;` × `.`), e por isso estão `SEMELHANTE`, com equivalência
provável. A medida literal subestima; a sem pontuação não decide sentido. A equivalência é da área.

### 2.5 Palavras por classificação

| Classificação | Unidades ativas (v3 · v2) | Simulados | Reais | Versão 2 | Versão 1 |
|---|---|---|---|---|---|
| EXATA | 33 · 17 | 561 (10%) | 1.530 (13%) | 581 | 581 |
| PARAMETRIZÁVEL | 61 · 46 | 3.567 (62%) | 1.770 (15%) | 3.510 | 3.510 |
| SEMELHANTE | 48 · 8 | 621 (11%) | 2.821 (24%) | 318 | 860 |
| INÉDITA | 158 · 70 | 989 (17%) | 4.628 (39%) | 1.329 | 787 |
| ESPECIALIZADA | 4 · 1 | 45 (1%) | 1.219 (10%) | 45 | 45 |

Nos simulados, o que se repete é **estrutura** (`PARAMETRIZÁVEL`, 62%): o sistema escreve a mesma frase com
outros valores. Nos reais, é **redação** (`SEMELHANTE`, 24%, e `EXATA`, 13%): o Cefor copia e adapta. As frases
escritas pelo sistema (origem C pura) continuam 16% das palavras dos simulados.

## 3. Sondagem e inventário: a mesma pergunta, duas medidas

A sondagem (18 editais, 95.768 palavras, reexecutada na rodada 2) achou **64%** das palavras em frases com
correspondência exata em outro edital, e 66% em frases recorrentes em edital de **outra família**. O inventário
acha **30%** do 59/2026 em linhas idênticas ao 28/2026.

Não se contradizem: a sondagem compara **frases** contra **17** outros editais; o inventário, **linhas inteiras**
contra **um**. A linha é mais longa que a frase, e basta uma palavra diferente para não casar. As duas medidas
apontam na mesma direção — o texto livre real se repete muito —, e o inventário diz onde: inscrição e documentos,
sorteio, recurso, matrícula, disposições finais e anexos (§2.4), as mesmas cláusulas que a sondagem apontava.

## 4. Respostas às perguntas da análise

**1. Quais conteúdos realmente se repetem?** No texto do sistema: as frases geradas de regra, entre editais do
sistema. No texto real: as cláusulas da casa — formato do envio, documentos, causas de indeferimento, sorteio e
semente, recurso e suas vedações, fraude e inexatidão, matrícula e regularização, certificado, gratuidade,
vigência, o Requerimento e a sua declaração.

**2. Com que frequência?** 8 unidades nos cinco editais, 10 em quatro, 28 em três, 76 em dois, 180 em um (§2.1).

**3. Que proporção do conteúdo?** Simulados entre si: 65% por função, 8% por texto. Reais contra simulados: 17% a
25% por função, 0% a 1% por texto. Reais entre si: 32% a 77% por função, 12% a 30% por texto (§2.2, §2.3).

**4. Quais diferenças são meramente textuais?** Além das da rodada 2: pontuação final e caixa entre 28 e 59
(LIB-0193, LIB-0198, LIB-0283); o texto do sistema e o do Cefor para a mesma regra (as 21 reclassificadas) —
**todas a confirmar**.

**5. Quais diferenças mudam as condições de tradução?** As da rodada 2, e as que os reais trouxeram na mesma
posição do documento: documentação irregular que **indefere a inscrição** (59) × que **impede a matrícula** (28)
(LIB-0243, LIB-0242); Requerimento incorreto que indefere **sem dizer** do recurso (28) × **sem recurso** (59)
(LIB-0200, LIB-0201); recurso “somente” contra dois atos × contra um (LIB-0252, LIB-0251); 15 × 30 suplentes
(LIB-0248, variável de condição); sorteio on-line × presencial (LIB-0240, LIB-0241); indeferido **por fenótipo** ×
**qualquer** indeferido mantido na ampla concorrência (LIB-0230, LIB-0045).

**6. Quais categorias têm maior potencial?** Ver §6.

**7. Quais exigiriam gravação específica quase sempre?** As da rodada 2, e nos reais: objetivo e matriz do curso,
heteroidentificação (instrução operacional da plataforma), definições legais de deficiência, Cronograma.

**8. A granularidade é plausível?** Como controle documental, sim, também no texto real: a cobertura fechou nos
dois, e o critério de desdobramento separou as regras diferentes. Como limite de tradução, continua sem resposta
— e agora há como testá-la: o vídeo do 28/2026 mostra **onde** uma tradução institucional cortou, agrupou e
reorganizou o edital.

## 5. Retificações

As quatro Retificações simuladas continuam sendo a única evidência de efeito de Retificação (rodada 2). As
reais **não foram lidas**: o 28/2026 tem uma Retificação (21/07) e um Comunicado de mudança da data de início
(24/08), ambos **posteriores ao vídeo em Libras** (05/05); o 59/2026 tem uma Retificação (30/07), publicada no
dia do resultado preliminar, e um comunicado de não realização do sorteio
([`editais/edital-28-2026/retificacoes.md`](../editais/edital-28-2026/retificacoes.md),
[`editais/edital-59-2026/retificacoes.md`](../editais/edital-59-2026/retificacoes.md)).

**Lacuna** que os reais abrem: um vídeo do edital que uma Retificação desatualiza. A página do 28/2026 não lista
vídeo da Retificação. O art. 30, VII, da LBI fala em tradução do edital **e de suas retificações**.

## 6. Reaproveitamento em três níveis

| Nível | O que se reaproveita | O que os cinco editais mostram | Plausibilidade documental (a testar) |
|---|---|---|---|
| **Roteiro** | a análise de preparação: o que a situação exige comunicar, em que relações, com que variantes, ambiguidades e perguntas | as quinze narrativas têm a mesma estrutura, simuladas e reais; o 59/2026 usa o roteiro do 28/2026 sem o bloco de cotas | **alta**, agora também no texto real |
| **Solução tradutória** | a escolha de expressão para um conteúdo que se repete | nos simulados, o texto fixo do sistema; nos reais, as cláusulas da casa, com texto idêntico entre 28 e 59 (§2.4) | **média a alta** para as cláusulas da casa, se a terminologia estiver decidida; **baixa** para levar uma solução do texto do sistema ao texto real |
| **Gravação** | o vídeo de um trecho | o Cefor já tem uma gravação integral do 28/2026; 30% das palavras do 59/2026 estão em linhas idênticas às do 28/2026 | **a medir**: pela primeira vez há o que medir — se trechos do vídeo do 28 servem ao 59. A decisão de encaixe é do profissional |

**Por intenção, à primeira análise:**

| Intenção | Roteiro | Solução tradutória | Gravação |
|---|---|---|---|
| Inscrição válida | comum aos cinco | formato do envio, documentos de todos, causas de indeferimento (iguais entre 28 e 59) | candidata nos blocos idênticos; não nos requisitos, prazos e documentos de cotas |
| Classificação e progressão | comum por forma de ordem | software e semente, análise dos sorteados, substituição (iguais entre 28 e 59) | candidata no bloco do software; não no local do sorteio, que muda e se contradiz |
| Contestar cada decisão | comum (objeto → prazo → canal → vedação → o que não cabe) | vedações e “não garante” (iguais entre 28 e 59) | candidata nas vedações; não no objeto e no prazo |

**Não há estimativa de economia** — nem de tempo de vídeo, nem de custo. O vídeo do 28/2026 tem 75 minutos e
corresponde a uma versão **anterior** à inventariada (8.611 palavras); os dois números descrevem uma tradução, e
não medem quanto dela outro edital aproveitaria.

## 7. Unidades e blocos para o piloto

Vinte unidades. A rodada 3 trocou a maior parte das do texto do sistema por cláusulas da casa, porque são elas
que se repetem no texto real.

**A. Cláusulas da casa (28 e 59)** — recorrência real, efeito jurídico claro, texto idêntico ou quase:

| # | Unidade | Classificação | Por quê |
|---|---|---|---|
| 1 | [LIB-0178](../catalogo/unidades/LIB-0178.md) Envio dos documentos: PDF, 7 MB, legível | EXATA | abre a lista de documentos dos dois editais |
| 2 | [LIB-0193](../catalogo/unidades/LIB-0193.md) Identificação: documentos aceitos | SEMELHANTE | difere só no ponto final; a cláusula mais difundida da sondagem |
| 3 | [LIB-0184](../catalogo/unidades/LIB-0184.md) Indeferimento por dados ou arquivo, sem recurso | SEMELHANTE | proibição expressa de recurso |
| 4 | [LIB-0186](../catalogo/unidades/LIB-0186.md) Indeferimento por formato ou validade | SEMELHANTE | par com a anterior: não diz nada do recurso |
| 5 | [LIB-0237](../catalogo/unidades/LIB-0237.md) Software do sorteio e semente | SEMELHANTE | conceito técnico; par com o texto do sistema (LIB-0026) |
| 6 | [LIB-0238](../catalogo/unidades/LIB-0238.md) Análise dos sorteados e substituição | EXATA | 104 palavras, idênticas |
| 7 | [LIB-0253](../catalogo/unidades/LIB-0253.md) O recurso não garante a alteração | EXATA | curta, idêntica |
| 8 | [LIB-0254](../catalogo/unidades/LIB-0254.md) Recurso sem fundamentação é indeferido | EXATA | regra embutida noutra linha, nos dois |
| 9 | [LIB-0149](../catalogo/unidades/LIB-0149.md) Recurso: não se aceita outra forma | SEMELHANTE | nos dois reais e no 92/2026 |
| 10 | [LIB-0279](../catalogo/unidades/LIB-0279.md) Inexatidão elimina | EXATA | consequência grave, texto idêntico |
| 11 | [LIB-0281](../catalogo/unidades/LIB-0281.md) Fraude: perda da vaga | EXATA | idem |
| 12 | [LIB-0298](../catalogo/unidades/LIB-0298.md) Declaração do Requerimento | EXATA | efeito penal; 99 palavras idênticas |

**B. Texto do sistema** — mantidas da rodada 2, para o caso de os editais passarem a sair do sistema:

| # | Unidade | Classificação | Por quê |
|---|---|---|---|
| 13 | [LIB-0034](../catalogo/unidades/LIB-0034.md) Limite de inscrições | EXATA | três simulados, texto idêntico |
| 14 | [LIB-0017](../catalogo/unidades/LIB-0017.md) Convocação por publicação | EXATA | par com a seguinte: regras opostas |
| 15 | [LIB-0079](../catalogo/unidades/LIB-0079.md) Convocação por mensagem individual | EXATA | idem |
| 16 | [LIB-0093](../catalogo/unidades/LIB-0093.md) Empate com excedente | EXATA | anáfora |
| 17 | [LIB-0123](../catalogo/unidades/LIB-0123.md) Empate estrito | EXATA | regra oposta |
| 18 | [LIB-0028](../catalogo/unidades/LIB-0028.md) Prazo de recurso do marco | PARAMETRIZÁVEL | três prazos, três nomes, e a ausência |

**C. Acessibilidade** — o público surdo é destinatário direto:

| # | Unidade | Classificação | Por quê |
|---|---|---|---|
| 19 | [LIB-0277](../catalogo/unidades/LIB-0277.md) Entrevista com o Napne | INÉDITA | onde o edital real trata de atendimento específico |
| 20 | [LIB-0107](../catalogo/unidades/LIB-0107.md) Atendimento especializado à PcD | INÉDITA | par do sistema |

Saíram da lista da rodada 2: LIB-0035, LIB-0064, LIB-0015, LIB-0078, LIB-0023, LIB-0092, LIB-0030, LIB-0124,
LIB-0050, LIB-0005, LIB-0128 e LIB-0068. Continuam no catálogo; só não são as mais promissoras diante do texto
real. LIB-0015 passou a `SEMELHANTE`: o 28/2026 tem a mesma regra em outra redação.

**Blocos comunicativos:** as narrativas de inscrição e de recurso do 28/2026 e do 59/2026, em par. É no par que se
vê o que de uma serve à outra.

## 8. O experimento mínimo

**Pergunta.** Para comunicar situações recorrentes do certame em Libras, o que se aproveita de um edital para
outro — roteiro, solução tradutória, gravação —, sem perda de compreensão nem de fidelidade jurídica?

**Material, agora disponível.** O 28/2026 e o 59/2026 inventariados, com as três narrativas cada; e **a tradução
contínua do 28/2026 que o Cefor já produziu** (o vídeo de 05/05/2026), que pode servir de referência, com
autorização.

**Antes de qualquer gravação nova, uma análise:** o profissional assiste ao vídeo do 28/2026 com a matriz de
cobertura ao lado e marca, linha a linha, onde a tradução começa e termina cada trecho, o que agrupou,
reorganizou, explicitou ou omitiu. É a primeira medida de granularidade real que o estudo pode ter, e responde à
pergunta 8 sem produzir vídeo.

**Três versões do mesmo conteúdo**, para cada narrativa do 59/2026:

1. **tradução contínua**, feita do zero pelo profissional;
2. **composição por unidades**, reaproveitando trechos da tradução do 28/2026 onde o texto é idêntico;
3. **composição por blocos comunicativos**, preparada a partir da narrativa, reaproveitando o roteiro e as
   soluções do 28/2026.

**O que medir:** compreensão (perguntas de verificação, com participantes surdos); fidelidade (revisão jurídica e da
área responsável); esforço de preparação, revisão e regravação, registrado pela equipe; e, por nível, quanto do 28
serviu ao 59.

**Critério.** O da rodada 2: se a versão 3 tiver compreensão e fidelidade equivalentes à 1, e o roteiro e as
soluções do 28 servirem ao 59 com pouca revisão, a hipótese ganha base para uma rodada maior. Se só a 1 for
adequada, o reaproveitamento se limita à preparação, e a biblioteca integrada não se justifica.

**Fora do experimento:** estimativa de custo, de tempo de vídeo ou de economia.

## 9. O que depende de profissionais e de outras áreas

- **Profissionais de Libras:** limites de vídeo; tratamento de tabelas, formulários e instruções operacionais;
  terminologia (inclusive a nova: heteroidentificação, semente, código de vaga, laudo e CID); a análise do vídeo do
  28/2026; validação de toda tradução e de todo reaproveitamento.
- **Área responsável pelas regras:** as 35 ambiguidades dos simulados e as 30 dos reais — destas, **13 defeitos do
  texto oficial** (contradições, remissões, datas) que precedem qualquer tradução nova —, e as equivalências
  `SEMELHANTE`.
- **Área jurídica:** o enquadramento de cada tipo de certame, inclusive cursos FIC; o recurso onde o edital o
  restringe (“somente”) e onde cala; a tradução das Retificações já publicadas.
- **A instituição:** autorização para usar o vídeo do 28/2026 no estudo.
- **Participantes surdos:** as perguntas de verificação, primeiro contra o vídeo existente.

## 10. Proposta para a rodada seguinte

Ainda com o 28/2026 e o 59/2026, **completar as versões**, com autorização para baixar:

| Documento | Tamanho | Para quê |
|---|---|---|
| Retificação do 28/2026, de 21/07/2026 (`publicacoes.ifes.edu.br`) | 111.411 bytes | o que mudou depois do vídeo em Libras |
| Comunicado de alteração do início do curso, 28/2026 (Google Drive) | não informado | idem |
| Retificação do 59/2026, de 30/07/2026 (`publicacoes.ifes.edu.br`) | 127.534 bytes | o que mudou com o certame em andamento |
| Comunicado de não realização do sorteio, 59/2026 (`publicacoes.ifes.edu.br`) | 54.487 bytes | o que a narrativa de classificação diz que não aconteceu |
| Anexos I e II do 59/2026, publicados à parte | 60.895 e 169.268 bytes | se são idênticos aos de dentro do PDF |

E as versões originais, se o Cefor as mantiver publicadas. Com elas, processar as Retificações pelo §3 do
[método](../metodo-incremental.md): seria a primeira medida da Retificação real de um edital que já tem tradução em
vídeo.

Depois, a alternativa longitudinal já proposta — o **149/2024**, o mesmo curso do 28/2026 dois anos antes — para
medir o que se aproveita do mesmo curso entre anos. E, como experimento complementar, a recomposição no sistema
(proposta da rodada 2), que agora tem com o que se comparar: o texto real inventariado.

## 11. Riscos e decisões pendentes

| Risco | Onde | Decisão pendente |
|---|---|---|
| O texto do sistema não é o texto real | §2.3 | se os editais passarem a sair do sistema, qual redação vale — a do sistema ou a da casa? (decisão de produto) |
| Texto da casa sem identidade | editais reais; o sistema, desde a `054` | cláusulas institucionais com identidade? (decisão de produto) |
| Defeitos do original traduzidos como norma | manifestos do 28/2026 e do 59/2026 | corrigir por Retificação antes de traduzir? |
| Vídeo desatualizado por Retificação | 28/2026 | traduzir as retificações (LBI, art. 30, VII)? |
| Texto fixo muda com o código | 49 commits no compositor desde 28/08 | gravar a versão do compositor em cada Publicação? |
| Tipos de certame com obrigações diferentes | auditoria, §13 | escopo de Libras por tipo de certame, inclusive FIC |
| Anexos e conteúdos fora do PDF | simulados; nos reais, publicados também à parte | entram no escopo? |
| Acessibilidade das etapas | 28/2026: entrevista por vídeo e canal de dúvidas sem Libras | fora do edital traduzido, mas no mesmo direito |
