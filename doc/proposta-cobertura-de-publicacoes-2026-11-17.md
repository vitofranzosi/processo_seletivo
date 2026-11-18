# Proposta mínima: completar a cobertura das publicações, sem arquitetura nova

Esta proposta continua [a análise da T15](analise-publicacoes-por-etapa-2026-11-17.md). **É
desenho, e não implementação**: nada aqui é spec aprovada. As decisões em aberto estão na seção 6 e
são da equipe.

Leitura do código da `main` em `31d93c47` (17/11/2026). Caminhos relativos a
`backend/processo_seletivo/`.

## 0. As orientações recebidas, e como cada uma foi atendida

| Orientação (parecer de 17/11) | Onde |
|---|---|
| Aproveitar a `148` para etapas decisórias, dizendo **exatamente** o que muda | Seção 2 |
| Preservar os marcos, sem um marco obrigatório por etapa pontuada | Seção 3 |
| Impedir a convocação **para a vaga** sem os pré-requisitos, sem bloquear agenda de entrevista ou prova | Seção 4 |
| Cenários completos: preliminar, consulta individual, recurso, julgamento, definitivo, avanço | Seção 5 |
| Sem arquitetura paralela de publicações e sem duplicar recursos | Seção 1 |
| Separar o ato público da consulta individual do candidato | Seções 1 e 2.3 |

## 1. O princípio: duas saídas que já existem, e só elas

Toda etapa de avaliação que pede publicidade sai do GPS por **uma de duas portas**, conforme o tipo
de resultado que produz.

| A etapa produz | Porta | Ato que já existe | O que muda |
|---|---|---|---|
| **Nota**, e com ela uma ordem: títulos, prova didática, entrevista pontuada | O **marco classificatório** que a lê | `PublicacaoResultado` (017) | Nada no código. Só o modo de modelar (seção 3) |
| **Condição**, deferida ou indeferida: análise documental, reserva, heteroidentificação PPI | O **resultado da etapa decisória** | `PublicacaoDasInscricoes` (148), hoje restrita a uma etapa | Generalizar (seção 2) |

Nas duas portas, quatro camadas continuam separadas, como já estão no código:

| Camada | Onde vive |
|---|---|
| Avaliação | `avaliacoes` |
| Resultado | `ResultadoEtapa`, individual, com motivo |
| Publicação | O ato, com conteúdo público e documento PDF/A |
| Comunicação | `avisos` |

**O ato público e a consulta individual já são coisas diferentes no GPS.** O ato publica nome e
protocolo de quem consta, sem motivo nem CPF. O candidato consulta o **próprio** resultado de cada
etapa, com o motivo, no acompanhamento. Quem autoriza a consulta é o ato
(`resultados/application/selectors.py:resultados_visiveis`): publicado o ato, o titular passa a ver
e a poder recorrer. Nada disso é novo, e a proposta não mexe nesse desenho.

**O recurso não se duplica.** Em todas as portas, o recurso é contra o `ResultadoEtapa` da pessoa,
com o mesmo julgamento (`recursos/application/julgar.py`) e a mesma régua de pendência.

## 2. Porta da condição: a `148` estendida a qualquer etapa decisória

### 2.1 O que já funciona por etapa, e não precisa mudar

Conferido no código. As peças que ligam o ato à consulta e ao recurso já são chaveadas por etapa
(`etapa_id`), e não pela cadeia única do Edital:

| Peça | Arquivo e função | Como já se comporta |
|---|---|---|
| Consulta individual | `resultados/application/selectors.py:_etapas_das_publicacoes_das_inscricoes` | Lê **todas** as etapas que algum ato publicou |
| Prazo de recurso | `recursos/application/interpor.py:_janela_da_publicacao_das_inscricoes` | Filtra os atos por `etapa_id=resultado.etapa_id` e soma a janela às dos marcos, valendo a mais generosa |
| Recursos pendentes | `recursos/application/selectors.py:recursos_pendentes_da_etapa(edital, etapa_id)` | Já é por etapa |
| Reavaliações pendentes | `reavaliacoes_pendentes(edital, etapa_id=…)` | Já é por etapa |
| O definitivo espera | `divulgacao/application/inscricoes.py:_disputa_em_aberto` | Recurso pendente, reavaliação e prazo correndo, todos por etapa |
| Recusa do recurso sem consulta | `interpor.py:_recusar_se_invisivel` | Passa a aceitar sozinha, assim que o ato existe |

Consequência: publicado o ato de uma etapa restrita, o candidato de PPI ou de reserva passa a ver o
próprio resultado e a poder recorrer, **sem mudança nenhuma em recursos**. É o que fecha a L2.

### 2.2 O que precisa mudar

Este é o trabalho real. É uma spec média, e não um ajuste, como o parecer advertiu.

| # | Hoje | Adaptação | Onde |
|---|---|---|---|
| A1 | **Uma cadeia por Edital**: o banco recusa uma segunda primeira publicação | Uma cadeia **por etapa**. A relação de recebidas, que não tem etapa, continua uma por Edital. É mudança de constraint em tabela append-only: nenhum dado se altera nem se exclui | `divulgacao/models.py`, `uq_publicacao_das_inscricoes_raiz` |
| A2 | Só aceita etapa decisória, eliminatória e **não restrita** | Aceitar qualquer etapa decisória eliminatória, restrita inclusive, e a que declara "retira da reserva" (164) | `divulgacao/domain/inscricoes.py:etapas_de_analise`; `_etapa_escolhida` |
| A3 | O universo é **toda** inscrição enviada do Edital. Foi por isso que a restrita ficou de fora: a ampla ficaria pendente para sempre | Universo = as inscrições que a etapa **alcança** (`editais/domain/alcance`) e que a progressão leva até ela (sem quem foi eliminado antes) | `divulgacao/application/inscricoes.py:_enviadas`, `projetar_agora` |
| A4 | Situação binária: deferida ou indeferida, conforme o resultado é `HABILITADA` | Ler também `RETIRADA_DA_RESERVA`. Para a lista reservada é "não consta"; a pessoa continua na ampla, e o ato não pode dizer que ela foi eliminada | `_resultados_vigentes`; `divulgacao/domain/inscricoes.py:projetar` |
| A5 | Três naturezas com nome de inscrição: recebidas, preliminar da análise das inscrições, **homologação das inscrições** | Na etapa, duas naturezas: **resultado preliminar** e **resultado definitivo da etapa {nome}**. O texto sai do vocabulário dos atos, e não de um rótulo novo em tela | `divulgacao/domain/vocabulario_dos_atos.py`; o documento em `divulgacao/infrastructure/documento_das_inscricoes.py` |
| A6 | Uma tela de publicação por Edital, e uma seção pública com um ato vigente | Publicar **por etapa**, numa tela por etapa (o padrão da agenda, também por etapa); a página pública lista um bloco por etapa | `interface/` (a tela da 148), `portal/views.py:_inscricoes_publicadas` e template |
| A7 | O andamento não tem célula para o resultado de etapa decisória | Uma célula "Publicar o resultado da etapa", reusando a mesma aferição. É leitura, e não motor | `interface/andamento.py` |

**Fora do mínimo**, e mantido assim de propósito:
- **Aviso por e-mail do resultado da etapa.** A origem `RESULTADO` exige marco (`ck_aviso_marco_da_origem`). Isso é da T16 e da T17 (seção 6, D5).
- **Qualquer mudança em recursos**, avaliação ou consolidação.

### 2.3 Dados pessoais, em especial na PPI

A fronteira pública da `148` é **de construção** (`divulgacao/domain/inscricoes.py`, D-010):

- o conteúdo público é montado só com **nome e protocolo de quem consta**, mais a **contagem** de
  quem não consta;
- motivo, CPF e parecer não entram na função que monta o conteúdo.

Na heteroidentificação, isso quer dizer que o ato público não nomeia quem teve a autodeclaração
recusada. A pessoa consulta a própria decisão, com o motivo, e os pareceres quando a spec 165 os
expõe (`avaliacoes.ExposicaoAoParecer`), e recorre pelo portal.

Isso **protege mais** do que a prática comum de publicar "indeferido" ao lado do nome. Se o Edital
mandar publicar os indeferidos, a forma é decisão da equipe (D1). O padrão proposto é manter a
fronteira atual.

## 3. Porta da nota: os marcos, sem obrigação de um por etapa

**O que um marco publica**, conferido em `classificacao/domain/combinacao.py:combinar`:

- é a **classificação**: posição, nome, protocolo, lista e pontuação combinada das etapas que ele
  enumera, por lista de concorrência;
- com uma etapa só, a pontuação publicada é a nota daquela etapa (operação média, ou soma
  normalizada pela soma dos pesos), ou a nota multiplicada pelo peso (soma sem normalização);
- o arredondamento é o do marco;
- o marco não publica "a nota" fora de uma ordem;
- quem foi eliminado, por nota mínima ou por etapa anterior, não aparece no ato público. Vê o
  próprio resultado na consulta individual.

**Duas formas legítimas, e quem escolhe é o Edital**:

| O Edital prevê | Modelagem | Publicações |
|---|---|---|
| **Uma classificação** que combina títulos e didática | Um marco que enumera as duas etapas | Um resultado preliminar e um definitivo. O candidato vê **cada** nota na consulta individual (`resultados_visiveis` libera cada etapa que o marco enumera) e pode recorrer de cada uma. Não há publicação intermediária artificial |
| **Resultado de cada prova** antes da seguinte | Um marco por prova que pede publicação, mais o marco final. A mesma etapa pode ser enumerada por mais de um marco | Uma classificação por prova, mais a final |

No segundo caso há dois detalhes de modelagem:
- se o marco da prova decide quem vai à prova seguinte (corte que governa a etapa), ele é o **marco intermediário** da spec 133, e não convoca para a vaga;
- se não decide nada, a validação só avisa ("classifica e não convoca", `milestone_without_cut_rule`).

**Sem mudança de código.** A ação é de roteiro: documentar as duas formas no guia de modelagem. A
validação já avisa sobre a etapa que não sai por porta nenhuma (`stage_without_result`). Fazer esse
aviso impedir a publicação é a decisão D4.

## 4. A trava da convocação para a vaga, e só dela

### 4.1 A regra

> **Convocar para ocupar a vaga exige que o resultado do marco de onde a pessoa sai seja
> definitivo e esteja publicado, sem prazo de recurso correndo e sem recurso pendente sobre ele.**

A agenda de entrevista ou prova é outro ato (`agendamento`, spec 167). Ela faz parte da avaliação e
**não** passa por esta trava.

### 4.2 Por que é pequena, e onde entra

- **A regra já existe escrita.** A destinação da vaga não preenchida (spec 155) a aplica, com três
  impedimentos nomeados e as frases prontas (`ocupacao/domain/destinacao.py:impedimentos`):
  - `RESULTADO_NAO_DEFINITIVO`;
  - `PRAZO_RECURSAL_ABERTO`;
  - `RECURSO_PENDENTE`.
- **Os fatos já são coletados**, por marco e por lista, em `interface/destinacao_da_vaga.py`, que os
  entrega como `fatos_externos`.
- **Só dois lugares gravam convocação:** `convocacao/application/convocar.py:convocar` e
  `convocar_em_sequencia`. Os dois já recusam o marco intermediário (spec 133), lado a lado
  (`marco_intermediario.recusar`). A trava entra **no mesmo ponto**, e alcança por construção os
  dois gestos que criam convocação: o dos titulares (`fluxo.py:convocar_titulares`, que chama
  `convocar_em_sequencia`) e a chamada individual (`fluxo.py:convocar_e_comunicar`, que chama
  `convocar`). O gesto das pendentes (`emitir_pendentes`) só comunica convocação que já existe, e
  não precisa dela.

**O ajuste de camada.** Hoje a coleta dos fatos está em `interface/`, e a convocação está em
`convocacao/application/`. A coleta desce para a camada de aplicação, para o comando não depender da
tela. É mudança de lugar, e não de regra.

**A tela antecipa a recusa.** A prévia da convocação e o andamento passam a mostrar o impedimento
**antes** do clique, com a data em que o prazo fecha. É o padrão das recusas nomeadas, e evita o
botão que só falha no envio.

### 4.3 O que a trava **não** cobre, e precisa de decisão

Lido o código, congelar a relação do sorteio também **não espera** o recurso contra a etapa de
habilitação (`sorteios/application/relacao.py` não consulta recurso nem prazo). A etapa de
habilitação é a que o método declara em `qualifyingStageId`, e a retirada da reserva entra por
`habilitacao.py:retiradas_antes`.

Recurso provido depois do sorteio obriga um **sorteio sucessor**, com relação e ocorrência novas.
Isso é muito mais caro do que esperar o prazo. A mesma trava, aplicada ao congelamento, é a
decisão D3.

## 5. Os cenários, do começo ao avanço

Legenda: **[hoje]** existe; **[A1–A7]** depende da seção 2; **[trava]** depende da seção 4.

### C1. TMD só com sorteio (sem reserva nem PPI)

1. Fim das inscrições. Relação de recebidas, opcional **[hoje]**.
2. A comissão congela a relação do sorteio. A página pública mostra a relação e o manifesto **[hoje]**.
3. O sorteio é constituído; o público verifica **[hoje]**.
4. Ordem emitida. Resultado **preliminar** publicado por lista **[hoje]**. Aviso `RESULTADO`, se a
   comissão confirmar **[hoje]**.
5. O candidato consulta e recorre dentro da janela do marco **[hoje]**.
6. Julgamento. Se for provido, o ato sucessor é emitido e o documento cita o recurso **[hoje]**.
7. Resultado **definitivo** publicado. O sistema recusa enquanto há recurso ou prazo **[hoje]**.
8. Apuração e convocação. A convocação **só passa daqui em diante [trava]**. Hoje ela passaria já no
   passo 4.
9. Publicação de convocados e aviso `CHAMADA` **[hoje]**.
10. Conferência de documentos e aviso `PENDÊNCIA`. Desfecho individual **[hoje]**.
11. Suplentes, chamada por chamada, cada uma com o próprio prazo **[hoje]**.

### C2. TMD com reserva ou PPI avaliada **antes** do sorteio

1. A etapa restrita alcança só as listas reservadas. Na PPI:
   - com comparecimento, a agenda é publicada e o aviso `AGENDA` sai sozinho **[hoje]**;
   - por vídeo, o aviso `PASSO` pede o envio **[hoje]**.
2. Avaliação e deliberação colegiada (spec 165); consolidação com o efeito declarado: elimina, ou
   retira da reserva (spec 164) **[hoje]**.
3. **Resultado preliminar da etapa** publicado, com o período de recurso escolhido no Cronograma.
   O público vê nome e protocolo de quem consta em cada lista reservada; quem não consta só entra
   na contagem **[A1–A6]**.
4. O candidato consulta a própria decisão, com o motivo, e recorre **[hoje, assim que o ato do
   passo 3 existir]**.
5. Julgamento; reavaliação, se determinada **[hoje]**.
6. **Resultado definitivo da etapa.** O sistema recusa enquanto há recurso, reavaliação ou prazo
   correndo **[hoje, pela regra da 148, já por etapa]**.
7. Congelamento da relação do sorteio. A lista reservada já sai sem quem foi retirado da reserva
   **[hoje]**. Esperar o passo 6 é a decisão **D3**.
8. Daí em diante, igual ao C1, do passo 3 em diante.

### C3. TMD com a análise de reserva ou PPI **na convocação** (sem etapa de avaliação)

1. Passos 1 a 9 do C1.
2. Documentos exigidos da convocação (specs 115 e 117). A conferência pede correção e o aviso
   `PENDÊNCIA` sai **[hoje]**.
3. Desfecho individual: indeferimento, reclassificação **[hoje]**. **Nada vai a público** (L5). O
   recurso e a publicação do desfecho ficam fora do GPS, se o Edital os exigir.

Para o TMD, C2 e C3 são a escolha de modelagem que depende da minuta (T04). **C2 é o único em que o
GPS cobre a publicidade da decisão e o recurso.**

### C4. Títulos e didática, com uma classificação final só

1. Títulos avaliados.
2. A agenda da didática é publicada; o aviso `AGENDA` sai **[hoje]**.
3. Didática avaliada e as duas etapas consolidadas.
4. O marco final emite a ordem. Resultado preliminar: o público vê a pontuação combinada; o
   candidato vê **cada** nota e recorre de cada uma **[hoje]**.
5. Julgamento, definitivo, convocação **[trava]**.

### C5. Títulos e didática, com resultado de títulos antes da didática

1. Marco "Classificação na prova de títulos", que enumera títulos. Se o corte dele governa a
   didática, é marco intermediário (spec 133).
2. Resultado preliminar e definitivo dos títulos **[hoje]**. A agenda da didática **não** espera o
   definitivo dos títulos pela trava; se deve esperar, é a decisão D6.
3. Marco final, que enumera títulos e didática: preliminar, recurso, definitivo, convocação
   **[trava]**.

## 6. Decisões da equipe

| # | Pergunta | Proposta padrão |
|---|---|---|
| D1 | No resultado de etapa restrita (PPI), o ato público nomeia **só quem consta**, como a 148, ou lista **todos** por protocolo com a situação? | Só quem consta, mais a contagem. A decisão individual fica na consulta do titular |
| D2 | Existe Edital que convoque para a vaga **sobre resultado preliminar**? Se sim, a trava ganha uma declaração do Edital que a dispensa | Não. Trava sem exceção na 1ª versão, até aparecer o caso |
| D3 | Congelar a relação do sorteio espera o resultado **definitivo** da etapa de habilitação? | Sim, se reserva ou PPI vierem antes do sorteio no TMD. Sorteio sucessor é o custo de não esperar |
| D4 | A etapa sem porta de saída (L1) passa de aviso a **impedimento** na publicação do Edital? | Avaliar depois do TMD. No TMD, o roteiro de modelagem basta |
| D5 | O resultado de etapa decisória ganha aviso por e-mail próprio? | Fica com T16 e T17, pela regra "e-mail quando o candidato precisa agir" |
| D6 | Agenda de prova seguinte a um marco intermediário espera o definitivo dele? | Não. A agenda é avaliação. Se o Edital disser o contrário, vira roteiro |
| D7 | A decisão de recurso (L3) e o desfecho da convocação (L5) ganham ato próprio? | Não no mínimo. No C2, a L3 fica coberta pelo resultado definitivo da etapa; no C1 e no C4, pelo definitivo republicado, que cita o recurso |

## 7. Ordem sugerida

**Frente 1, o TMD:**
1. Definir C1, C2 ou C3 com a minuta (T04).
2. Reproduzir a L4 na homologação. É formalidade: o código não tem a verificação.
3. A **trava** (seção 4). É pequena e vale para qualquer Edital.
4. Se for C2: a **148 estendida** (seção 2) e a D3.

**Frente 2, depois do TMD:**
1. O roteiro de modelagem da seção 3.
2. A D4.
3. As decisões D5 e D7.

Cada item da frente 1 é uma spec própria, pela prática de uma spec por sessão. A ordem só pesa porque a 148 estendida só é necessária se a minuta escolher o C2.
