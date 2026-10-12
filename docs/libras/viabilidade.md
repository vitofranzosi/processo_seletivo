# Viabilidade da hipótese: recorrência e reuso em Libras

**Análise revisada em 2026-10-11 (rodada 4), sobre a versão 3 do catálogo.** Baseada nos três editais **simulados**,
nos dois editais **reais** do Cefor inventariados por inteiro (28/2026 e 59/2026, agora com as versões reconstruídas
pelos atos), na sondagem em 18 editais reais, no protótipo da camada comunicativa e numa
[comparação focalizada](comparacao-focalizada/README.md) com dois editais técnicos do Ifes que têm vídeo em Libras
(19/2026 e 46/2026). As análises anteriores estão preservadas: rodadas [1](historico/viabilidade-rodada-1.md),
[2](historico/viabilidade-rodada-2.md) e [3](historico/viabilidade-rodada-3.md).

> **O que a rodada 4 corrigiu.** A versão anterior afirmava que a hipótese de reuso do texto do sistema “não se
> confirma” e que o reaproveitamento de gravações “só é discutível no texto da casa”. As duas frases excediam a
> medida: os 0% e 1% eram palavras em **linhas inteiras** coincidentes, comparadas **dentro da unidade** atribuída
> pelo catálogo, contra **todo** o texto simulado — inclusive o texto livre que a auditoria redigiu. Coincidência
> literal em português não mede equivalência de sentido, e menos ainda se uma tradução ou uma gravação servem a
> outro edital. A medida foi refeita, com o conjunto restrito às frases que o sistema gera (§2.3), e nenhuma
> conclusão sobre tradução ou gravação se tira dela.

## A decisão em uma frase

**Há base para um experimento com profissionais de Libras e participantes surdos, e não há base para desenvolver
agora uma biblioteca audiovisual integrada ao sistema — porque nada foi validado, linguística nem operacionalmente.**
Os percentuais de coincidência em português descrevem o texto; não restringem nem confirmam o potencial de
compor traduções por blocos. O que o estudo pode afirmar é documental: há situações comunicativas recorrentes,
algumas com regra equivalente e outras com o mesmo assunto e regra diferente — e a diferença entre as duas pode
estar em três palavras ([eliminação](comparacao-focalizada/eliminacao.md), alínea g). Saber se roteiro, solução
tradutória ou gravação se aproveitam é o que o [protocolo profissional](comparacao-focalizada/protocolo-profissional.md)
foi desenhado para medir.

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

Reproduzíveis com `python3 docs/libras/ferramentas/medir.py` ([`ferramentas/`](ferramentas/README.md)).

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

Três comparações, com conjuntos diferentes. Nas três, o denominador são as palavras do edital real (28/2026: 8.611;
59/2026: 3.375, com o cabeçalho em imagem da página 9, incluído na rodada 4), e o que se mede é **coincidência literal
em português** — nunca equivalência de sentido, nem reaproveitamento de tradução.

**(a) Contra o corpus simulado inteiro, dentro da unidade.** Conjunto: todas as linhas dos três simulados — texto
gerado pelo sistema **e** texto livre redigido pela auditoria. Uma linha real conta se alguma linha simulada **da
mesma unidade** tiver o mesmo texto normalizado. É a medida que a rodada 3 publicou, agora com a atribuição correta.

| Edital | Mesma unidade num simulado | Linha idêntica num simulado |
|---|---|---|
| 28/2026 | 17% | 0% |
| 59/2026 | 25% | 1% |

**(b) Contra as frases que o sistema gera, sem restrição de unidade.** Conjunto: as 97 linhas dos simulados cuja
unidade tem origem **C pura** (frase escrita pelo sistema a partir de regra) — 910 palavras, 32 frases de quatro
palavras ou mais, 20 unidades. Ficam de fora as linhas de origem mista (com texto livre) e as de origem A (cabeçalho,
numeração, rótulos).

| Edital | Em linha idêntica a uma linha gerada | Em frase idêntica a uma frase gerada | Em linha com a mesma função de uma frase gerada |
|---|---|---|---|
| 28/2026 | 0,0% | 0,0% | 0,5% (43 palavras) |
| 59/2026 | 0,0% | 0,0% | 0,3% (10 palavras) |

Das 20 unidades do conjunto, duas aparecem nos reais: a reversão por ausência de aprovados (LIB-0015) e a ordem por
sorteio (LIB-0025). **Limite:** “mesma função” depende da atribuição do catálogo, que cria unidade nova quando muda o
destinatário, a condição ou a consequência — e as cláusulas reais do sorteio, por exemplo, ganharam unidades próprias
(LIB-0236 a LIB-0240) por dizerem mais, ou outra coisa. Se dizem **o mesmo** que as frases do sistema, em parte, é
pergunta de sentido, e não de catálogo.

**(c) Entre os dois reais, dentro da unidade.**

| Edital | Mesma unidade no outro real | Idêntico ao outro real | Quase idêntico (sem caixa e pontuação) |
|---|---|---|---|
| 28/2026 | 32% | 12% | 15% |
| 59/2026 | 77% | 31% | 40% |

**O que estas medidas permitem dizer (Fato):** a redação que o sistema gera não aparece literalmente nos editais reais
do Cefor; e o Cefor repete a própria redação entre editais. **O que não permitem dizer:** que o texto do sistema
comunique outra coisa, que uma tradução de um não sirva ao outro, ou que uma gravação do texto da casa sirva ao
seguinte. A [comparação focalizada](comparacao-focalizada/eliminacao.md) mostra por que a coincidência literal engana
nas duas direções: textos iguais em doze alíneas e diferentes, com efeito oposto, na décima terceira.

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

**3. Que proporção do conteúdo?** Em coincidência literal: simulados entre si, 65% por função e 8% por texto; reais
contra os simulados, 17% a 25% por função e 0% a 1% por texto, e nada contra as frases que o sistema gera; reais entre
si, 32% a 77% por função e 12% a 31% por texto (§2.2, §2.3). **Nenhum desses números é proporção de conteúdo
reaproveitável em Libras.**

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
dois, e o critério de desdobramento separou as regras diferentes. Como limite de tradução, continua sem resposta.
Os três vídeos institucionais observados rotulam na tela a **seção** do edital ([`videos.md`](comparacao-focalizada/videos.md)),
e não o item: o rótulo é um ponto observado, e não um limite de corte. Onde a tradução se divide de fato é o que o
profissional precisa marcar, assistindo, e só nos trechos cuja versão é conhecida.

## 5. Retificações

As quatro Retificações simuladas mostraram os tipos de efeito (rodada 2). As reais, lidas na rodada 4, mostram outra
coisa: **a versão consolidada que o órgão publica não é a soma dos atos.**

- **28/2026.** A Retificação nº 01 (21/07) passou o Quadro 2 de 40 para 60 vagas por polo, de 280 para 420 no total. A
  versão “retificado em 24/08” traz o Cronograma do Comunicado de 24/08 (início em 01/09) e **continua com 40 vagas e
  280 no item 4.1** ([`editais/edital-28-2026/retificacoes.md`](editais/edital-28-2026/retificacoes.md)).
- **59/2026.** A Retificação de 30/07 mudou os Eventos 7, 8 e 11; a versão consolidada do mesmo dia, cinco horas
  anterior, incorpora o 7 e o 8 e não o 11 (início em 10/08, e não em 24/08). A página do processo informa ainda um
  terceiro prazo de recurso ([`editais/edital-59-2026/retificacoes.md`](editais/edital-59-2026/retificacoes.md)).
- **46/2026.** O arquivo que a página chama de edital de 03/08 é uma versão de 14/09 que incorpora as três erratas; a
  original não está mais disponível ([`comparacao-focalizada/fontes.md`](comparacao-focalizada/fontes.md)).

**Consequência para a tradução.** Traduzir “o edital” pede, antes, saber **qual texto vigora** — e, em dois dos três
casos, os documentos oficiais divergem entre si. Para comparar um vídeo com o texto, é preciso saber que versão o vídeo
traduz: no 28/2026, provavelmente a original de 07/04, que não foi obtida; no 46/2026, uma versão anterior à
publicação, desconhecida. Diferença posterior ao vídeo **não é omissão**.

**Lacuna:** as páginas não listam vídeo em Libras das Retificações. O art. 30, VII, da LBI fala em tradução do edital
**e de suas retificações**.

## 6. Reaproveitamento em três níveis

Três coisas diferentes podem ser reaproveitadas. **O estudo não mediu nenhuma delas**: o que segue é o que a
documentação sugere testar, e não plausibilidade demonstrada.

| Nível | O que se reaproveita | O que a documentação mostra | O que falta para saber |
|---|---|---|---|
| **Roteiro (preparação)** | a análise de preparação: o que a situação exige comunicar, em que relações, com que variantes, ambiguidades e perguntas | as quinze narrativas têm a mesma estrutura, simuladas e reais; na comparação focalizada, as situações se descrevem pelos mesmos campos nos quatro editais reais | que o profissional prepare um edital a partir do material do outro e registre o que usou e o que refez (protocolo, fase 2) |
| **Solução tradutória** | a escolha de expressão para um conteúdo que se repete | situações com regra equivalente e português idêntico (19 × 46), com regra equivalente e português diferente (28 × 19 e 46), e com o mesmo assunto e regra diferente | a resposta do profissional, situação por situação: a mesma, adaptada ou outra |
| **Gravação** | o trecho de vídeo | três vídeos institucionais, de pessoas e versões diferentes, com a seção do edital rotulada na tela | as condições G1 a G4 do protocolo — inclusive a **G2**, que testa gravações de blocos de mesmo sentido escritos de outra forma, e a **G3**, o controle |

A coincidência literal **não decide** nenhum dos três: um trecho de português idêntico pode exigir outra gravação
(contexto, referente, pessoa sinalizante), e um bloco de português diferente pode, em tese, servir com a mesma gravação
se o sentido for o mesmo — é o que a G2 testa.

**Não há estimativa de economia** — nem de tempo de vídeo, nem de custo — nesta análise.

## 7. Unidades e blocos para o piloto

Vinte unidades, escolhidas por **recorrência documental** e efeito jurídico claro. A escolha não pressupõe que se
aproveitem em Libras: é o conjunto em que a pergunta se faz. A rodada 3 trocou parte das do texto do sistema por
cláusulas da casa, porque são elas que se repetem literalmente nos editais reais; a rodada 4 não muda a lista, e
acrescenta, como blocos do piloto, as situações da comparação focalizada.

**A. Cláusulas da casa (28 e 59)** — recorrência real, efeito jurídico claro, texto idêntico ou quase:

| # | Unidade | Classificação | Por quê |
|---|---|---|---|
| 1 | [LIB-0178](catalogo/unidades/LIB-0178.md) Envio dos documentos: PDF, 7 MB, legível | EXATA | abre a lista de documentos dos dois editais |
| 2 | [LIB-0193](catalogo/unidades/LIB-0193.md) Identificação: documentos aceitos | SEMELHANTE | difere só no ponto final; a cláusula mais difundida da sondagem |
| 3 | [LIB-0184](catalogo/unidades/LIB-0184.md) Indeferimento por dados ou arquivo, sem recurso | SEMELHANTE | proibição expressa de recurso |
| 4 | [LIB-0186](catalogo/unidades/LIB-0186.md) Indeferimento por formato ou validade | SEMELHANTE | par com a anterior: não diz nada do recurso |
| 5 | [LIB-0237](catalogo/unidades/LIB-0237.md) Software do sorteio e semente | SEMELHANTE | conceito técnico; par com o texto do sistema (LIB-0026) |
| 6 | [LIB-0238](catalogo/unidades/LIB-0238.md) Análise dos sorteados e substituição | EXATA | 104 palavras, idênticas |
| 7 | [LIB-0253](catalogo/unidades/LIB-0253.md) O recurso não garante a alteração | EXATA | curta, idêntica |
| 8 | [LIB-0254](catalogo/unidades/LIB-0254.md) Recurso sem fundamentação é indeferido | EXATA | regra embutida noutra linha, nos dois |
| 9 | [LIB-0149](catalogo/unidades/LIB-0149.md) Recurso: não se aceita outra forma | SEMELHANTE | nos dois reais e no 92/2026 |
| 10 | [LIB-0279](catalogo/unidades/LIB-0279.md) Inexatidão elimina | EXATA | consequência grave, texto idêntico |
| 11 | [LIB-0281](catalogo/unidades/LIB-0281.md) Fraude: perda da vaga | EXATA | idem |
| 12 | [LIB-0298](catalogo/unidades/LIB-0298.md) Declaração do Requerimento | EXATA | efeito penal; 99 palavras idênticas |

**B. Texto do sistema** — mantidas da rodada 2, para o caso de os editais passarem a sair do sistema:

| # | Unidade | Classificação | Por quê |
|---|---|---|---|
| 13 | [LIB-0034](catalogo/unidades/LIB-0034.md) Limite de inscrições | EXATA | três simulados, texto idêntico |
| 14 | [LIB-0017](catalogo/unidades/LIB-0017.md) Convocação por publicação | EXATA | par com a seguinte: regras opostas |
| 15 | [LIB-0079](catalogo/unidades/LIB-0079.md) Convocação por mensagem individual | EXATA | idem |
| 16 | [LIB-0093](catalogo/unidades/LIB-0093.md) Empate com excedente | EXATA | anáfora |
| 17 | [LIB-0123](catalogo/unidades/LIB-0123.md) Empate estrito | EXATA | regra oposta |
| 18 | [LIB-0028](catalogo/unidades/LIB-0028.md) Prazo de recurso do marco | PARAMETRIZÁVEL | três prazos, três nomes, e a ausência |

**C. Acessibilidade** — o público surdo é destinatário direto:

| # | Unidade | Classificação | Por quê |
|---|---|---|---|
| 19 | [LIB-0277](catalogo/unidades/LIB-0277.md) Entrevista com o Napne | INÉDITA | onde o edital real trata de atendimento específico |
| 20 | [LIB-0107](catalogo/unidades/LIB-0107.md) Atendimento especializado à PcD | INÉDITA | par do sistema |

Saíram da lista da rodada 2: LIB-0035, LIB-0064, LIB-0015, LIB-0078, LIB-0023, LIB-0092, LIB-0030, LIB-0124,
LIB-0050, LIB-0005, LIB-0128 e LIB-0068. Continuam no catálogo; só não são as mais promissoras diante do texto
real. LIB-0015 passou a `SEMELHANTE`: o 28/2026 tem a mesma regra em outra redação.

**Blocos do piloto (rodada 4):** as situações de [Eliminação](comparacao-focalizada/eliminacao.md) e de
[Inscrição](comparacao-focalizada/inscricao.md), distribuídas pelas condições G1 a G4 do
[protocolo](comparacao-focalizada/protocolo-profissional.md) — inclusive pares de regra equivalente e português
diferente entre o 28/2026 e os editais técnicos.

## 8. O experimento mínimo

O experimento agora tem desenho próprio: [`comparacao-focalizada/protocolo-profissional.md`](comparacao-focalizada/protocolo-profissional.md).
Em resumo:

- **Antes:** alinhar a versão que cada vídeo traduz; decidir a terminologia; obter autorização da instituição para
  qualquer recorte (os vídeos estão sob CC BY-NC-ND).
- **Fase 1 — sem gravação nova:** o profissional assiste aos trechos de Eliminação e Inscrição do 19/2026 e do 46/2026
  (e do 28/2026, onde a versão é conhecida) e marca, situação por situação, onde a tradução começa e termina, o que
  traz, o que reorganiza e de que depende.
- **Fase 2 — os três níveis, separados:** preparação, solução tradutória e gravação, esta em quatro condições —
  **G1** português idêntico e regra equivalente; **G2** regra equivalente e português diferente; **G3** mesmo assunto e
  regra diferente (controle); **G4** valor diferente.
- **Fase 3 — opcional:** compreensão com participantes surdos, só com perguntas de estado “definitiva”.

**Critério, mais modesto que o da rodada 3.** Um resultado positivo em G1 e G2 justifica uma rodada maior, com
gravações planejadas para reaproveitamento. Um resultado negativo registra os limites **daquela tentativa** — vídeos
não feitos para segmentação, versões não confirmadas, poucos avaliadores — e não basta para concluir que a biblioteca
não se justifica.

## 9. O que depende de profissionais e de outras áreas

- **Profissionais de Libras:** limites de vídeo; tratamento de tabelas, formulários e instruções operacionais;
  terminologia (inclusive a nova: heteroidentificação, semente, código de vaga, laudo e CID); a análise do vídeo do
  28/2026; validação de toda tradução e de todo reaproveitamento.
- **Área responsável pelas regras:** as 35 ambiguidades dos simulados e as 30 dos reais — destas, **13 defeitos do
  texto oficial** (contradições, remissões, datas) que precedem qualquer tradução nova —, e as equivalências
  `SEMELHANTE`.
- **Área jurídica:** o enquadramento de cada tipo de certame, inclusive cursos FIC; o recurso onde o edital o
  restringe (“somente”) e onde cala; a tradução das Retificações já publicadas.
- **A instituição:** autorização para usar os vídeos do 19/2026, do 46/2026 e do 28/2026 no estudo, e para qualquer
  recorte; identificação da versão que cada vídeo traduz; e a resposta às divergências entre versões oficiais.
- **Participantes surdos:** as perguntas de verificação, primeiro contra o vídeo existente.

## 10. Proposta para a rodada seguinte

1. **Fase 1 do protocolo**, com dois profissionais de Libras: Eliminação e Inscrição, 19/2026 × 46/2026, e as situações
   G2 com o 28/2026.
2. **Resposta da área** às pendências registradas — as vagas do 28/2026, o início do 59/2026, a alínea g do 46/2026, o
   texto traduzido pelo vídeo do 46/2026 —, sem a qual parte das comparações fica marcada como “versão não confirmada”.
3. **A versão original do 28/2026** (07/04), se o Cefor a tiver, para delimitar o que o vídeo de 05/05 traduz.

Fica para depois: a alternativa longitudinal (149/2024, o mesmo curso do 28/2026) e a recomposição no sistema, como
experimento complementar.

## 11. Riscos e decisões pendentes

| Risco | Onde | Decisão pendente |
|---|---|---|
| A redação do sistema não é a dos editais reais | §2.3 (coincidência literal; o sentido não foi avaliado) | se os editais passarem a sair do sistema, qual redação vale — a do sistema ou a da casa? (decisão de produto) |
| A versão consolidada não é a soma dos atos | §5 | qual texto vigora, e como o órgão publica a consolidação |
| A versão traduzida pelo vídeo não é conhecida | 28/2026, 46/2026 | registrar, em cada vídeo, a versão que ele traduz |
| Texto da casa sem identidade | editais reais; o sistema, desde a `054` | cláusulas institucionais com identidade? (decisão de produto) |
| Defeitos do original traduzidos como norma | manifestos do 28/2026 e do 59/2026 | corrigir por Retificação antes de traduzir? |
| Vídeo desatualizado por Retificação | 28/2026 | traduzir as retificações (LBI, art. 30, VII)? |
| Texto fixo muda com o código | 49 commits no compositor desde 28/08 | gravar a versão do compositor em cada Publicação? |
| Tipos de certame com obrigações diferentes | auditoria, §13 | escopo de Libras por tipo de certame, inclusive FIC |
| Anexos e conteúdos fora do PDF | simulados; nos reais, publicados também à parte | entram no escopo? |
| Acessibilidade das etapas | 28/2026: entrevista por vídeo e canal de dúvidas sem Libras | fora do edital traduzido, mas no mesmo direito |
