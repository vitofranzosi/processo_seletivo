> **Registro histórico.** Esta é a análise de viabilidade da **rodada 2** (versão 2 do catálogo, 154
> identificadores), preservada sem alterações de conteúdo. Ela foi substituída por [`../viabilidade.md`](../viabilidade.md),
> que acrescenta os editais reais 28/2026 e 59/2026. Os links abaixo apontam para o estado atual dos arquivos:
> unidades citadas aqui podem ter mudado de classificação na rodada 3, e o *Histórico* de cada uma diz quando.

# Viabilidade da hipótese: recorrência e reuso em Libras

**Medição de 2026-10-11 — versão 2 do catálogo (rodada 2).** Baseada nos três editais **simulados** do
corpus, numa sondagem fora do corpus em editais reais do Cefor e no protótipo da camada comunicativa. Os
números da versão 1 aparecem ao lado; a análise da rodada 1, inteira, está em
[`historico/viabilidade-rodada-1.md`](viabilidade-rodada-1.md).

> **O que mudou desde a rodada 1.** O método foi corrigido (regras diferentes deixaram de se agrupar por
> posição; diferenças só de redação passaram a equivalências a confirmar), e por isso as métricas mudaram.
> A conclusão se manteve na direção e mudou na pergunta: a rodada 1 tratava a recomposição de variáveis como
> a pergunta decisiva; esta separa **três** possibilidades de reaproveitamento — roteiro, solução tradutória e
> gravação —, que se avaliam de modo diferente e podem valer mesmo quando a gravação precisa ser refeita. E
> acrescenta o contexto legal: a obrigação de tradução completa em Libras não é a mesma para todo tipo de
> certame.

## A decisão em uma frase

**Há base para um experimento com profissionais de Libras e participantes surdos; não há base para
desenvolver uma biblioteca audiovisual integrada ao sistema.** O corpus mostra recorrência de **função e
estrutura** alta e de **texto idêntico** baixa; a sondagem sugere que, na prática, o texto livre se repete
muito entre editais reais. Nenhum desses números mede tradução reutilizável validada. O ganho mais provável
— a verificar — está em reaproveitar **roteiros e soluções tradutórias** de situações recorrentes do
certame; o reaproveitamento de **gravações** é o mais incerto dos três.

---

## 1. A amostra, e o que ela não permite dizer

| | Corpus | Sondagem complementar |
|---|---|---|
| O quê | 3 editais publicados pelo sistema (91/2026, 92/2026, 01/2026) e 4 Retificações | 18 editais reais do Cefor, 2024–2026 |
| Natureza | **simulados**: texto livre redigido pela auditoria do PDF e pelo `seed_demo` | **reais**, não produzidos pelo sistema, fora do repositório |
| Tipos de certame | ingresso em curso (91), seleção de bolsistas (92), contratação de professor substituto e técnico (01) | ingresso em cursos, bolsistas e outras seleções |
| Inventário | integral, com unidade por linha e narrativas | nenhum: comparação automática de frases |
| Serve para | medir o que o sistema escreve sozinho e o que a estrutura repete | estimar se o texto livre se repete entre editais de verdade |
| Não serve para | medir recorrência de texto livre; comparar tipos de certame diferentes como se fossem equivalentes | dizer algo sobre equivalência de sentido, ou sobre outras Unidades |

**Três editais é pouco**, e de três tipos de certame diferentes — o que reduz a recorrência esperável e
impede tratar uma frase igual como equivalente sem olhar o tipo (ver [`auditoria-sistema.md`](../auditoria-sistema.md), §13).

## 2. Métricas do corpus

Reproduzíveis com `python3 docs/libras/ferramentas/medir.py` ([`ferramentas/`](../ferramentas/README.md)).

### 2.1 Unidades e ocorrências

| Medida | Versão 1 | **Versão 2** |
|---|---|---|
| Identificadores | 126 | **154** (142 ativos, 12 desdobrados) |
| Ocorrências (sem rodapé) | 374 | **377** (3 regras embutidas ganharam unidade) |
| Unidades novas por edital (91 · 92 · 01) | 72 · 49 · 4 | **72 · 62 · 7** |
| Unidades em 1 · 2 · 3 editais | 69 · 31 · 24 | **92 · 26 · 22** |

Desdobrar regras diferentes aumenta as unidades de ocorrência única: é o efeito esperado de deixar de
agrupar o que não é equivalente.

### 2.2 Proporção das palavras

| Edital | Palavras | Unidade recorre em outro edital (v2 · v1) | Texto idêntico em outro edital | Repetido no próprio edital |
|---|---|---|---|---|
| 91/2026 | 1.436 | **61%** · 71% | 11% | 4% |
| 92/2026 | 3.711 | **63%** · 68% | 5% | 25% |
| 01/2026 | 654 | **86%** · 93% | 17% | 12% |
| **Corpus** | **5.801** | **65%** · 72% | **8%** | — |

- **Unidade que recorre** mede recorrência de **função**.
- **Texto idêntico** mede recorrência de **texto** (numeração de item e alínea desconsideradas).
- **Nenhum dos dois mede tradução reutilizável.** O primeiro diz que há uma comunicação do mesmo tipo noutro
  edital; o segundo, que as palavras são as mesmas. Se o vídeo, a solução ou o roteiro servem, só o
  experimento diz.

### 2.3 Palavras por classificação

| Classificação | Unidades ativas | Palavras v2 | Palavras v1 |
|---|---|---|---|
| EXATA | 17 | 581 (10%) | 581 |
| PARAMETRIZÁVEL | 46 | 3.510 (61%) | 3.510 |
| SEMELHANTE | 8 | 318 (5%) | 860 |
| INÉDITA | 70 | 1.329 (23%) | 787 |
| ESPECIALIZADA | 1 | 45 (1%) | 45 |

As frases escritas pelo sistema (origem C pura) são **16%** das palavras — o único texto que se repete por
construção. A origem do texto, medida com o próprio compositor ([`auditoria-sistema.md`](../auditoria-sistema.md),
§1), não mudou: redação livre 58%, 64% e 33%; texto fixo do sistema 32%, 27% e 55%.

### 2.4 Texto idêntico por família (versão 2)

| Família | Unidades | Ocorr. | Em ≥ 2 editais | Palavras com texto idêntico em outro edital |
|---|---|---|---|---|
| ATO — abertura e fecho | 9 | 59 | 8 | 33% (o fecho coincide só porque os três foram gerados no mesmo dia) |
| CLA — classificação | 18 | 33 | 8 | 21% |
| INS — inscrição | 9 | 12 | 2 | 16% |
| CON — convocação e matrícula | 7 | 8 | 1 | 11% |
| DOC — documentos | 20 | 36 | 8 | 6% |
| CRO — cronograma | 18 | 34 | 7 | 4% |
| PER — Perfis e vagas | 15 | 142 | 8 | 1% |
| GER, OFE, REQ, AFI, ETA, REC | 10, 4, 16, 7, 2, 6 | — | 2, 0, 2, 0, 2, 0 | 0% |

## 3. Sondagem complementar: o texto livre se repete entre editais reais?

Reproduzível com `python3 docs/libras/ferramentas/sondagem_editais_reais.py`, **se** os PDFs listados em
[`ferramentas/referencia/sondagem-entrada.json`](../ferramentas/referencia/sondagem-entrada.json) estiverem
disponíveis (estão fora do repositório). Reexecutada em 2026-10-11, rodada 2, com o mesmo resultado.

| Medida (95.768 palavras, 18 editais) | Resultado |
|---|---|
| Palavras em frases com correspondência exata em outro edital | **64%** |
| Palavras em frases recorrentes (≥ 80% das sequências de quatro palavras) | 78% |
| Idem, **em edital de outra família** | **66%** |
| Faixa por edital (outra família) | de 19% (69/2026) a 92% (35/2026) |

As cláusulas mais difundidas: documentos de identificação aceitos; isenção de responsabilidade por dados
incorretos; explicação do sorteio e da semente; canal e vedações de recurso; fraude; consentimento de
dados pessoais; tradução juramentada; alistamento militar.

**Limites.** Mede texto, não sentido (“Anexo I” e “Anexo V” contam como iguais); a correspondência é contra o
documento inteiro; uma Unidade só; editais de tipos de certame diferentes comparados entre si. Nenhuma unidade
`LIB-` deriva da sondagem.

## 4. Respostas às perguntas da análise

**1. Quais conteúdos realmente se repetem?** Com texto idêntico, as frases que o sistema escreve a partir de
regra e o cabeçalho do órgão. Com a mesma função e outro texto, quase tudo o que tem estrutura. Na prática
(sondagem), também cláusulas livres de inscrição, documentos, recurso, fraude e disposições finais.

**2. Com que frequência?** 22 unidades estão nos três editais, 26 em dois, 92 em um só (§2.1).

**3. Que proporção do conteúdo?** 65% das palavras por função, 8% por texto idêntico (§2.2).

**4. Quais diferenças são meramente textuais?** Numeração de item e alínea, número da tabela, valores das
variáveis **de valor** (datas, quantidades), e — a confirmar — redações diferentes do mesmo efeito: canal de
inscrição (LIB-0031), remissão aos requisitos do Perfil (LIB-0012), requisito de graduação (LIB-0021), nome do
comprovante de CPF (LIB-0037), forma de envio da identificação (LIB-0128), documento de conclusão (LIB-0129).

**5. Quais diferenças mudam as condições de tradução?** As de destinatário, modalidade normativa, condição ou
consequência, ainda que pequenas na letra: experiência “no magistério” × “superior” × “básico ou superior,
ou vínculo a pós-graduação” (LIB-0139, LIB-0141, LIB-0142); canal de dúvidas exclusivo × facultativo (LIB-0127,
LIB-0151); desistência × não manifestação presumida como desistência (LIB-0134, LIB-0150); falsidade ×
inexatidão ou falsidade (LIB-0135, LIB-0154); reversão por ausência × pelo saldo; empate estrito × com
excedente; dias corridos × úteis; prazo declarado × negativa expressa × **ausência de cláusula**; e as
variáveis **de condição** das unidades parametrizáveis (caráter da Etapa, Etapa governada, admite recurso). O
tipo de certame também muda: a mesma frase pode ter outro peso jurídico.

**6. Quais categorias têm maior potencial?** Ver §6, separado por nível de reaproveitamento.

**7. Quais exigiriam gravação específica quase sempre?** Oferta e público, requisitos de Perfil, atribuições,
descrição e preâmbulo, justificativa de Retificação, tabelas de Perfis e de vagas, Cronograma completo, e
todas as narrativas no seu conjunto.

**8. A granularidade é plausível?** **Como controle documental, sim. Como limite de tradução, não se sabe,
e a revisão da rodada 1 sugere que não é o ponto de partida.** A unidade média tem 15 palavras; muitas só
têm sentido com outras (empate depois do corte, remissões, tabelas). O protótipo de narrativas propõe outra
granularidade para a preparação — a situação do candidato, com 3 a 14 enunciados —, também a testar.

## 5. Retificações

As quatro Retificações do corpus (os `retificacoes.md` de cada edital) mostram requisitos que qualquer
biblioteca teria de atender: mudança pequena com efeito grande (renumeração de oito seções no 92/2026);
texto igual com efeito diferente (o corte do 91/2026; o corte fixo do 01/2026 diante de mais vagas);
retirada de cláusula, que não retira direito previsto em lei (92/2026); e dois documentos válidos, um
vigente (01/2026, vigência futura). Nas narrativas, cada Retificação aparece no enunciado que ela afeta.

## 6. Reaproveitamento em três níveis

Três coisas diferentes podem ser reaproveitadas, e a repetição de texto não diz nada sobre a terceira.

| Nível | O que se reaproveita | O que o corpus mostra | Plausibilidade documental (a testar) |
|---|---|---|---|
| **Roteiro** | a análise de preparação: o que a situação exige comunicar, em que relações, com que variantes, ambiguidades e perguntas | as nove narrativas têm a mesma estrutura nos três editais; dentro de cada intenção, os tipos de enunciado se repetem (canal, prazo, documentos por destinatário, limite; universo, ordem, corte, empate, suplência; objeto, prazo, canal, vedação, ausência) | **alta**, mesmo entre tipos de certame diferentes, desde que o conteúdo de cada enunciado seja refeito |
| **Solução tradutória** | a escolha de expressão para um conteúdo que se repete: um termo, uma frase do sistema, uma relação (reserva → ampla), uma forma de comunicar ausência | 17 unidades `EXATA`, quase todas texto fixo do sistema (16% das palavras); terminologia comum a todos os editais; 8 unidades `SEMELHANTE` com equivalência a confirmar | **média**: depende de a terminologia estar decidida e de a solução valer em contextos diferentes; nos `PARAMETRIZÁVEL`, só quando as variáveis de condição coincidem |
| **Gravação** | o vídeo de um trecho | nenhuma gravação existe; texto idêntico entre editais é 8% das palavras; quase todo trecho repetido carrega datas, números ou nomes, ou depende do trecho anterior | **baixa** fora do texto fixo do sistema; incerta mesmo nele, porque o encaixe de um vídeo noutro contexto é decisão linguística e de produção |

**Por intenção, à primeira análise:**

| Intenção | Roteiro | Solução tradutória | Gravação |
|---|---|---|---|
| Inscrição válida | estrutura comum aos três editais | limite de inscrições, cabeçalhos de documentos, Requerimento, ausência de conferência | improvável por inteiro: prazos, Perfis e documentos mudam |
| Classificação e progressão | estrutura comum por forma de ordem (sorteio, pontuação) | frases do marco, do corte, do empate e da continuação; reversão | o bloco do corte tem variáveis de condição; o método do sorteio muda a cada edital |
| Contestar cada decisão | estrutura comum (objeto → prazo → canal → vedação → ausência) | regras comuns de canal e vedação, frequentes na prática | pouco provável: cada objeto tem prazo próprio |

**Não há estimativa de economia** — nem de tempo de vídeo, nem de custo — nesta análise: nada nela a
fundamenta, e a repetição textual não é medida de reaproveitamento audiovisual.

## 7. Unidades e blocos para o piloto

Vinte unidades, escolhidas por recorrer entre editais ou ser texto fixo do sistema, ter efeito jurídico claro
e exercitar os três níveis. Correções da rodada 2: LIB-0036 e LIB-0061, desdobradas, deram lugar a LIB-0128
e LIB-0149.

| # | Unidade | Classificação | Por quê |
|---|---|---|---|
| 1 | [LIB-0034](../catalogo/unidades/LIB-0034.md) Limite de inscrições | EXATA | três editais, texto idêntico |
| 2 | [LIB-0035](../catalogo/unidades/LIB-0035.md) Documentos de todos (cabeçalho) | EXATA | três editais; unidade curta de rótulo |
| 3 | [LIB-0064](../catalogo/unidades/LIB-0064.md) Requerimento no ato da inscrição | EXATA | dois editais |
| 4 | [LIB-0017](../catalogo/unidades/LIB-0017.md) Convocação por publicação | EXATA | par com a seguinte: regras opostas |
| 5 | [LIB-0079](../catalogo/unidades/LIB-0079.md) Convocação por mensagem individual | EXATA | dois editais |
| 6 | [LIB-0015](../catalogo/unidades/LIB-0015.md) Reversão por ausência de aprovados | EXATA | par com a seguinte: diferença jurídica fina |
| 7 | [LIB-0078](../catalogo/unidades/LIB-0078.md) Reversão pelo saldo | EXATA | idem |
| 8 | [LIB-0023](../catalogo/unidades/LIB-0023.md) Marcos por Perfil separadamente | EXATA | frase de alcance |
| 9 | [LIB-0092](../catalogo/unidades/LIB-0092.md) Corte com quantidade fixa | PARAMETRIZÁVEL | base do bloco do corte (9–13) |
| 10 | [LIB-0093](../catalogo/unidades/LIB-0093.md) Empate com excedente | EXATA | anáfora |
| 11 | [LIB-0123](../catalogo/unidades/LIB-0123.md) Empate estrito | EXATA | regra oposta |
| 12 | [LIB-0030](../catalogo/unidades/LIB-0030.md) Continuação admitida | EXATA | completa o bloco |
| 13 | [LIB-0124](../catalogo/unidades/LIB-0124.md) Continuação não admitida | EXATA | regra oposta |
| 14 | [LIB-0028](../catalogo/unidades/LIB-0028.md) Prazo de recurso do marco | PARAMETRIZÁVEL | três prazos e três nomes; e a ausência |
| 15 | [LIB-0050](../catalogo/unidades/LIB-0050.md) Evento: período de inscrições | PARAMETRIZÁVEL | data como variável de valor |
| 16 | [LIB-0005](../catalogo/unidades/LIB-0005.md) Abertura de seção | PARAMETRIZÁVEL | navegação |
| 17 | [LIB-0128](../catalogo/unidades/LIB-0128.md) Identificação com foto (forma de envio) | SEMELHANTE | equivalência a confirmar; cláusula mais difundida nos editais reais |
| 18 | [LIB-0149](../catalogo/unidades/LIB-0149.md) Recurso: não se aceita outra forma | INÉDITA | vedação frequente nos editais reais |
| 19 | [LIB-0068](../catalogo/unidades/LIB-0068.md) Casos omissos | PARAMETRIZÁVEL | fórmula com uma variável |
| 20 | [LIB-0107](../catalogo/unidades/LIB-0107.md) Atendimento especializado à PcD | INÉDITA | o público surdo é destinatário |

E três **blocos comunicativos**, um por intenção prototipada: a narrativa de recurso do 91/2026 (dois objetos e
uma ausência), a de classificação do 01/2026 (duas regras de empate opostas) e a de inscrição do 92/2026
(requisitos por grupo de Perfis).

## 8. O experimento mínimo

**Pergunta.** Para comunicar situações recorrentes do certame em Libras, o que se aproveita de um edital
para outro — roteiro, solução tradutória, gravação —, sem perda de compreensão nem de fidelidade jurídica?

**Material.** Dois editais **reais** de contexto próximo, com anexos e Retificação (§10), inventariados e com as
três narrativas; a terminologia decidida antes.

**Três versões do mesmo conteúdo**, para cada narrativa:

1. **tradução contínua**, feita do zero pelo profissional;
2. **composição por unidades** do catálogo atual, gravadas uma vez e recompostas;
3. **composição por blocos comunicativos**, preparada a partir da narrativa, reaproveitando o roteiro e as
   soluções do primeiro edital no segundo.

**O que medir:** compreensão (perguntas de verificação, com participantes surdos); fidelidade (revisão
jurídica e da área responsável); esforço de **preparação**, de **revisão** e de **regravação** de cada versão,
registrado pela equipe; e, por nível, quanto do primeiro edital serviu no segundo — roteiro, solução,
gravação.

**Critério.** Se a versão 3 tiver compreensão e fidelidade equivalentes à 1, e o roteiro e as soluções do
primeiro edital servirem ao segundo com pouca revisão, a hipótese ganha base para uma rodada maior. Se só a 1
for adequada, o reaproveitamento se limita à preparação (roteiros), e a biblioteca integrada não se justifica.
A versão 2 mede se a granularidade documental atual tem algum papel na produção.

**Fora do experimento:** estimativa de custo, de tempo de vídeo ou de economia.

## 9. O que depende de profissionais e de outras áreas

- **Profissionais de Libras:** limites de vídeo; organização espacial; tratamento de tabelas, variáveis,
  remissões e códigos; terminologia; paráfrases; validação de toda tradução e de todo reaproveitamento.
- **Área responsável pelas regras:** as 35 ambiguidades das narrativas e as equivalências `SEMELHANTE`.
- **Área jurídica:** o enquadramento de cada tipo de certame; recurso onde o edital cala; o estatuto do vídeo
  da declaração do Requerimento.
- **Participantes surdos:** se as perguntas de verificação medem compreensão, e a avaliação das três versões.

## 10. Proposta para a rodada seguinte

Dois editais **reais e originais**, de contexto próximo — ingresso em curso do Cefor, os dois sob a LBI,
art. 30, VII —, ambos com anexos no próprio PDF e Retificação, e ambos com sorteio:

| Edital | Por quê | O que a amostra tem | O que falta obter |
|---|---|---|---|
| **28/2026** — Pós-graduação lato sensu em Informática na Educação, EaD (Cefor/Ifes) | é o edital real em que o cenário A foi calibrado: permite comparar real × simulação; seis anexos no PDF (cronograma, autodeclarações, consentimento de dados) | versão “retificado em 24.08.2026”, 23 páginas | a versão original e o ato da Retificação, para comparar versões |
| **59/2026** — Curso de Língua Brasileira de Sinais (Libras) Iniciante A1 | ingresso em curso de curta duração, contexto próximo e diferente do 28; público com interesse direto em Libras; o “ANEXO I – CRONOGRAMA (RETIFICADO)” marca a Retificação no próprio documento | versão “retificado em 30/07/2026”, 11 páginas, 2 anexos | a versão original e o ato da Retificação |

Alternativa longitudinal: o **149/2024** (o mesmo curso do 28/2026, dois anos antes, retificado em 31/01/2025)
mediria o que se aproveita do mesmo curso entre anos. Os PDFs estão na amostra do projeto (`~/Downloads`),
fora do repositório, e são públicos nos sítios do Cefor e do Ifes.

**Recomposição no sistema, como experimento complementar.** Recompor os dois editais no sistema e publicá-los
num banco isolado permitiria medir o que o compositor escreve sozinho num edital real. Mas o documento
recomposto **não é o ato oficial**: o sistema reescreve partes (frases geradas, tabelas, numeração) e o
resultado precisa ser comparado com o original, com as diferenças registradas trecho a trecho, e nunca
substituí-lo no inventário.

## 11. Riscos e decisões pendentes

| Risco | Onde | Decisão pendente |
|---|---|---|
| Texto fixo muda com o código | 49 commits no compositor desde 28/08 | gravar a versão do compositor em cada Publicação? |
| Numeração posicional e digitada | 92/2026 v2 | como os vídeos navegam |
| Vocabulário do sistema no ato | auditoria do PDF de 08/10, §5 | reescrever as frases antes de qualquer gravação |
| Texto livre sem identidade | sistema, desde a `054` | cláusulas institucionais com identidade? (decisão de produto) |
| Tipos de certame com obrigações diferentes | auditoria, §13 | escopo de Libras por tipo de certame |
| Anexos e conteúdos fora do PDF | anexos, resultado, avisos, convocação | entram no escopo? |
| Corpus simulado | esta rodada | rodada com editais reais (§10) |
