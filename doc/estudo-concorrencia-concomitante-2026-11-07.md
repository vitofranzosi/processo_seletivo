# Estudo — concorrência concomitante: o desfecho de uma lista e as outras listas da pessoa

**Data**: 07/11/2026 · **Base**: `main` em `cd1d46d9` · **Natureza**: investigação, só documento. Nenhum
código de produto, FR, migration ou banco de origem foi alterado.

O ponto de partida são dois casos. O primeiro é o de Helena, no Edital 93/2026 do banco de
demonstração, contado no capítulo 10 do
[guia dos documentos](guia-documentos-no-gps-2026-11-06/index.html). O segundo é o cenário F do
[estudo do sorteio do Edital 35/2026](estudo-sorteio-edital-35-2026-11-05.md) (§3.7, §5, Q6–Q8). Os
dois são a mesma família de problema: **o GPS trata cada lista como um mundo à parte**, e a mesma
pessoa concorre em duas.

> **Governança.** Este documento registra fatos medidos, leituras de norma e recomendações. Nada
> aqui vira escopo por estar escrito: decidir a regra é do usuário e, onde o Edital não responde, da
> Instituição. As perguntas estão na §9. Elas usam o prefixo `QC` para não colidir com as `Q` do
> estudo do Edital 35, nem com a varredura de `test_citacoes_de_requisito.py`.

Os caminhos de código são relativos a `backend/processo_seletivo/`. Todos os personagens são
fictícios, como o banco de demonstração.

**Fontes.**
- O código e os testes na `main` em `cd1d46d9`.
- As specs 016, 019, 050, 095, 097, 098 e 122.
- Os Editais 28, 35 e 57/2026 e o 46/2026, lidos em PDF fora do repositório com `pdftotext -layout`.
- Uma cópia descartável do `gps_docs_demo` (`createdb -T`), migrada para a `main`. As simulações
  rodaram em clones dessa cópia; o `gps_docs_demo` não foi tocado.

Os roteiros e a saída estão em
[`estudo-concorrencia-concomitante-2026-11-07/reproducao/`](estudo-concorrencia-concomitante-2026-11-07/reproducao/).

---

## 1. Resumo

| Situação | Conclusão |
|---|---|
| Confirmado por teste | **O caso estático está certo.** Um cotista entre os titulares da ampla não é contado na reservada. A vaga dele continua na reserva e vai ao próximo autodeclarado, sem movimento de vaga (FR-252 a FR-254). |
| Confirmado por reprodução | **A desistência na ampla devolve a pessoa à reservada.** Helena desistiu na ampla. A PPI passou a tê-la como titular, a "Convocar titulares" a propôs, e o gesto a **convocou**. Com o aceite dela, a PPI ficou com **duas pessoas com aceite numa vaga só**, e o número continuou "1 ocupada". |
| Confirmado por reprodução | **A mesma pessoa ocupa duas vagas.** Ícaro regularizou pela PcD e depois foi chamado e aceitou pela ampla. Passou a contar nas duas: ampla 2 de 2 e PcD 1 de 1. É o cenário F do Edital 35, agora reproduzido no 93. |
| Confirmado por reprodução | **A desistência na reservada não alcança a ampla.** Quem desistiu pela PcD continua chamável pela ampla, e o GPS o convoca. |
| Só no código | **O retorno à reservada foi escolhido num comentário, e não numa FR.** `ocupacao/application/selectors.py:611` diz que, sem aplicar os efeitos da ampla, quem desiste ficaria "fora das duas listas". A escolha é do commit `bcc8b9f1` (019) e não aparece em nenhuma spec. |
| Só no código | **A reservada não envelhece quando a ampla muda.** A apuração reservada não guarda quem ocupava a ampla, e não há causa de obsolescência para isso. A fila e a prévia, porém, recalculam na hora. Por isso a proposta muda sem ato na PPI, e a apuração continua "vigente". |
| No Edital | **A desistência é "de realizar o curso".** O cancelamento por inércia é "considerado desistente e terá sua matrícula cancelada". Os dois textos falam da pessoa no curso, e não de uma lista. O único desfecho que o Edital limita a uma lista é o **indeferimento da autodeclaração**, que deixa a pessoa "apenas na lista de ampla concorrência" (8.10). |
| Pendente | **Não atendimento, reclassificação e a pessoa que aceitou a reservada e é alcançada pela ampla** não têm texto que responda. São decisões institucionais (§9). |

**Recomendação, em uma linha.** Decidir primeiro a regra (§9). A recomendação técnica é tratar a
desistência e a inércia como **da pessoa no marco**, que alcança todas as listas dela. O indeferimento
seria separado pela causa, e a reclassificação ficaria na lista. A isso se soma uma **invariante de
uma ocupação por pessoa** no Perfil e marco, que o banco não garante hoje. Até lá, a mitigação é
operacional (§8.1).

---

## 2. Os dois casos

### 2.1 Edital 93/2026 — Helena

Um Perfil, um marco, três recortes. Ampla tem 2 vagas, PPI 1 e PcD 1. O Perfil **não declara reversão**.

| Recorte | Ordem que progrediu | Convocações e desfechos (estado do `gps_docs_demo`) |
|---|---|---|
| Ampla | Helena, Fábio, Davi, Ícaro | Helena, vaga inicial → **desistência expressa**. Fábio, vaga inicial → aceite. Davi, suplência → em aberto |
| PPI | Helena, Carla | Carla, vaga inicial → aceite |
| PcD | Bruno, Gael, Ícaro | Bruno, vaga inicial → indeferimento. Gael, suplência → em aberto |

Helena é PPI e foi a 1ª da ampla. Pela regra do 8.9, ela não contou na PPI, e a vaga da PPI foi de
Carla, que aceitou. Depois, Helena desistiu na ampla. O que o GPS mostra hoje na PPI, sem ninguém ter
praticado ato nesse recorte:

| Leitura da PPI | Valor | De onde vem |
|---|---|---|
| Apuração vigente | 1 publicada, 1 efetiva, 1 ocupada, **sem causa de obsolescência** | ato de 06/11, às 22h45, quatro segundos antes da desistência |
| Quem ocupa pela ampla, hoje | só Fábio | `ocupantes_da_ampla` aplica a desistência de Helena |
| Titulares recalculados | **Helena** | a janela de 1 vaga, agora sem exclusão |
| Quem ocupa, recalculado | **Helena e Carla** | Helena por ser titular; Carla pela inclusão do aceite |
| Fila | Helena | Helena não tem convocação na PPI |
| "Convocar titulares" | **Convocar 1 titular — Helena** | `previa_dos_titulares` |

"Ocupadas 1" é `min(2, 1)`: o teto de `apurar` (FR-253a) esconde a segunda pessoa.

### 2.2 Edital 35/2026 — cenário F (do estudo de 05/11)

- C7 é o 1º da PPI e está fora das quatro vagas da ampla.
- Ele aceita a vaga PPI. Depois, desistências na ampla fazem a fila da ampla chegar até ele.
- O GPS o convoca pela ampla, como suplência, e registra o aceite.
- C7 passa a contar nas duas: ampla 4 de 4 e PPI 1 de 1. São cinco pessoas em seis vagas, e C11, a
  próxima da PPI, nunca é alcançada.

O cenário B2 da §4 reproduz o mesmo efeito no 93.

---

## 3. A regra atual, reconstituída

### 3.1 O mecanismo em quatro peças

1. **A janela de titulares da reservada exclui quem ocupa pela ampla.**
   - `sequencia_por_pessoa` e `titulares_iniciais` estão em `ocupacao/domain/apuracao.py:100` e `:123`.
   - A exclusão corre **antes** da janela, e é a única que corre (FR-252).
   - "Quem ocupa pela ampla" é `ocupantes_pela_ampla` (`apuracao.py:219`), lida por
     `ocupacao/application/selectors.py:571`. São os titulares da ampla **mais e menos os efeitos da
     ampla**: quem desistiu na ampla deixa o conjunto, e quem aceitou como suplente entra.
2. **Os efeitos de um desfecho só alcançam o próprio recorte.**
   - `EFEITO_POR_DESFECHO` (`convocacao/domain/nomes.py:55`): aceite e regularização incluem; os
     outros cinco excluem.
   - O efeito é gravado com o `lista_id` da convocação (`desfechar.py:157`), e cada apuração lê só os
     efeitos do seu recorte.
   - `ocupantes` (`apuracao.py:187`) aplica as inclusões **depois** da janela. Por isso **a exclusão
     concomitante não alcança quem aceitou na reservada**: o aceite o põe de volta, mesmo que ele
     ocupe também a ampla.
3. **A fila é por recorte, e a exclusão concomitante só existe na reservada.**
   - `contexto_do_recorte` (`convocacao/application/selectors.py:319`) aplica `ocupantes_da_ampla`
     apenas quando há `lista_id`.
   - `_situacoes` (`:506`) lê só as convocações do recorte. "Servido", "encerrado" e "em aberto" são,
     portanto, por lista.
   - A unicidade do banco também é por recorte: `uq_convocacao_raiz_por_recorte` e
     `..._e_lista`, em `convocacao/models.py:166-171`, e FR-268.
   - Nada impede convocar, ou contar como ocupante, a mesma Inscrição em dois recortes do mesmo
     Perfil e marco.
4. **A apuração reservada não congela a ampla.**
   - O universo gravado (`ocupacao/application/emissao.py:262`) guarda ordem, corte, movimentos,
     efeitos e acréscimos, mas **não** quem ocupava a ampla.
   - As seis causas de `causas_de_obsolescencia` (`ocupacao/application/selectors.py:125`) não incluem
     "a ampla mudou".
   - A `apuracao_seguinte` do desfecho (`desfechar.py:277`) reemite só o recorte do desfecho.
   - Resultado: a reservada continua "vigente" com o número antigo, enquanto a fila e a prévia
     (`contexto_do_recorte`, `previa_dos_titulares`) recalculam com a ampla de agora.

Há uma assimetria que a reprodução tornou visível. **A habilitação atravessa as listas, e o desfecho
não.** O Resultado da Etapa é da Inscrição, e não do recorte. A regularização pela PcD
(`desfechar._suceder_o_resultado`) habilitou Ícaro também para a ampla, e foi isso que o tornou
chamável ali.

### 3.2 O que está comprovado por teste

| Fato | Teste |
|---|---|
| Cotista entre os titulares da ampla não conta na reservada, e a vaga reservada segue aberta (4/4/1 e 1/1/0) | `tests/integration/ocupacao/test_concomitancia.py::TestOCaminhoPositivo::test_o_cotista_ocupa_pela_ampla_e_nao_conta_na_reservada` |
| A concomitância não cria movimento de vaga, e reapurar não duplica | mesmo arquivo, `test_a_concomitancia_nao_cria_movimento_de_vaga` e `test_reapurar_nao_duplica_nem_muda_o_numero` |
| Reserva esgotada pela concomitância cede o saldo sob reversão por saldo, uma vez só | mesmo arquivo, `TestEsgotamentoDaReserva` |
| A fila da reservada só tem quem concorre nela; a desistência na reservada abre vaga na mesma lista; o aceite do suplente fecha o número; nada se move para a ampla | `tests/integration/convocacao/test_suplencia.py` (SC-086, FR-270, FR-280) |
| Reversão: declaração, linha geral recebe, sem atravessar Perfil | `tests/integration/ocupacao/test_reversao.py` |
| Quem desiste na ampla sai de "quem ocupa pela ampla"; o suplente que aceita entra | `tests/unit/ocupacao/test_ocupantes_pela_ampla.py::test_desistencia_e_aceite_da_019` |
| Quem ocupa pela ampla sai antes da janela da fila reservada | `tests/unit/convocacao/test_fila.py::test_quem_ocupa_pela_ampla_sai_antes_da_janela` |

**Nenhum teste cobre um desfecho numa lista e a leitura da outra.** A busca não achou nada sobre
desistência, aceite ou indeferimento observados no outro recorte. O efeito na ampla está testado,
na unidade. A consequência na reservada não está.

### 3.3 O que está só no código

- **A desistência na ampla devolve a pessoa à reservada.** É o comentário de
  `ocupacao/application/selectors.py:611`, sem FR que o diga.
- **A exclusão concomitante não alcança aceite nem regularização registrados na reservada**, pela
  ordem de `ocupantes`. Ver o cenário B2.
- **"Ocupadas" satura no teto e esconde duas pessoas numa vaga.** O teto de `apurar` vem da FR-253a,
  escrita para suplentes na faixa, e não para este caso.
- **A fila da ampla não exclui quem está servido na reservada.**
- **O titular eliminado na ampla continua descontado da reservada.** É o achado R-002 da 095,
  preservado pela D-005 da 095.

### 3.4 O que está só na spec

- **FR-252 a FR-254 (016)** tratam do caso estático: quem ocupa pela ampla não é computado na
  reservada, a vaga fica na reserva, e "dentro das vagas nas duas listas" registra pela ampla. As
  FRs não dizem o que acontece **quando a ocupação da ampla muda**.
- **FR-275, FR-279 e FR-280 (019)**: a vaga liberada é chamada "no mesmo recorte", e a chamada "MUST
  NOT atravessar recorte". O texto pensa na **vaga**. A pessoa, que atravessa os recortes, não
  aparece.
- **FR-278 e FR-278a (019)**: o efeito vale "na emissão seguinte", e nenhum número diferente do
  apurado é afirmado antes dela. A prévia da PPI que muda com a ampla está **em tensão com o espírito
  da FR-278a**. O número exibido continua o apurado, mas a proposta de convocação já é a nova, sem
  emissão nem causa dita.
- **FR-268 (019)**: uma convocação vigente por Inscrição **no mesmo recorte**. Entre recortes, a spec
  não diz nada.
- **DP-1 e DP-2 (095)**, que continuam pendentes:
  - a faixa da reservada conta quem ocupa pela ampla;
  - "há quem ocupar" conta quem nunca ocupará a reservada.
- **098 e 122** só citam o comportamento atual (concomitância "só na ocupação"). Não decidem nada
  sobre desfechos.

---

## 4. Reprodução no 93 (clones descartáveis)

As simulações chamaram os comandos de domínio (`convocar`, `desfechar`, `convocar_titulares`,
`emitir_apuracao`) como o gestor da demonstração.

- **Uma alteração, só no processo da simulação:** a guarda documental do aceite (115, FR-3592) foi
  desligada. Ela está fora do escopo deste estudo, e não lê nem escreve ocupação ou fila.
- **Nenhum e-mail saiu.** O backend de desenvolvimento imprime a mensagem no console, e ela apareceu
  na saída.

| Cenário | O que se fez | O que o GPS respondeu |
|---|---|---|
| **A** — Helena, continuação | Reapurar a PPI; confirmar "Convocar titulares"; aceite de Helena na PPI | Reapuração: 1/1/1. O gesto **convoca Helena como titular** (vaga inicial) e envia "Você foi convocado". O aceite é registrado. A PPI fica com **Carla e Helena com aceite**, e ainda "1 ocupada". Helena desistiu do curso pela ampla e está matriculável pela PPI. |
| **B2** — dupla ocupação | Gael desiste na PcD; Ícaro (eliminado na Etapa) é chamado para regularizar na PcD e regulariza; Davi desiste na ampla; Ícaro é chamado pela ampla e aceita | A PcD fica com Ícaro, 1/1. A ampla **aceita convocar Ícaro como suplência**, e o aceite a deixa 2/2 com Fábio e Ícaro. Reapurada a PcD: **1/1, com Ícaro**. A mesma pessoa em duas vagas, e ninguém mais na PcD. |
| **C** — desistência na reservada | Ícaro é chamado para regularizar na PcD e **desiste**; Davi desiste na ampla; Ícaro é chamado pela ampla | A ampla **convoca Ícaro**. A desistência pela PcD não o alcança na ampla. |
| **C2** — variante | Ícaro regulariza na PcD; tentativa de inércia sem motivo de sucessão; Davi desiste; Ícaro é chamado pela ampla | A inércia é recusada por falta de motivo de sucessão. Isso é recusa de forma, sem relação com a concomitância. Ícaro, ocupando a PcD, é **convocado pela ampla como suplência**. |
| **D2** — ordem inversa | Ícaro regulariza pela **ampla** primeiro; Gael desiste na PcD; tentativa de chamar Ícaro pela PcD | Recusa `lista_alcancada_esgotada`: a PcD **pula** quem ocupa pela ampla. A PcD fica 0/1, com vaga sem dono e ninguém na faixa. Este é o caminho que já funciona. |

O inventário do `gps_docs_demo`
([`reproducao/inventario.sql`](estudo-concorrencia-concomitante-2026-11-07/reproducao/inventario.sql),
só leitura) não acha nenhuma pessoa com convocação vigente em dois recortes. O caso de Helena é
**latente**: a PPI a propõe, mas ninguém a convocou. Nenhum ato gravado precisa ser revisto nesse
banco.

---

## 5. Matriz de cenários

**Papéis.** P concorre na ampla (A) e numa reservada (R).
- **TA**: está entre os titulares da ampla.
- **SA**: está na faixa da ampla, além das vagas.
- **TR** e **SR**: o mesmo para R. Uma pessoa TA nunca é TR hoje, porque R a exclui da janela.
- **TR-posição**: a pessoa estaria entre os titulares de R pela posição, se não fosse a exclusão.

**Desfechos que excluem.** Desistência expressa, indeferimento, não atendimento, inércia e
reclassificação têm o **mesmo efeito** na ocupação: exclusão no recorte. Diferem em três pontos:
- a reclassificação move a pessoa para o fim da fila (FR-283);
- a inércia exige que a pessoa já ocupe (`_recusar_inercia_sem_ocupacao`);
- o indeferimento não muda o Resultado da Etapa, e a pessoa continua habilitada para as outras listas.

Na coluna "Edital", **F** é texto explícito, **I** é inferência forte do texto e **P** é pendente,
sem texto.

| # | P em A / R | Desfecho, e onde | Contados hoje | Propostos hoje | Dupla ocupação ou vaga sem dono | O que o Edital diria |
|---|---|---|---|---|---|---|
| 1 | TA / TR-posição | nenhum | A: P. R: o próximo autodeclarado | R chama o próximo | Não | **F** — 8.8 e 8.9: classificado na ampla, abre vaga ao próximo autodeclarado. Comprovado por teste. |
| 2 | TA / TR-posição | **desistência em A** (Helena) | A: sem P. R: P como titular + quem aceitou R, com o teto escondendo | R propõe **P como titular** | **Sim**: duas pessoas com aceite numa vaga de R se P aceitar (cenário A) | **I** — "desista de realizar o curso" (8.8): a desistência é do curso. P não deveria voltar a R. O 8.9 fixa a exclusão por "sorteados dentro do número de vagas", e não pela ocupação. |
| 3 | TA / TR-posição | indeferimento em A, por documentação geral | como 2 | como 2 | como 2 | **I** — 8.6 (35) e 8.3: "a matrícula não será efetivada". Os documentos gerais são os mesmos para as duas listas. |
| 4 | TA / TR-posição | não atendimento em A | como 2 | como 2 | como 2 | **P** — nenhum texto. A chamada é para a matrícula no curso, o que sugere alcançar a pessoa. |
| 5 | TA / TR-posição | **inércia em A** | como 2 | como 2 | como 2 | **I** forte — 11.3: "considerado desistente e terá sua matrícula cancelada". A matrícula é uma só. |
| 6 | TA / TR-posição | reclassificação em A | A: P no fim da fila. R: P titular | R propõe P | Sim, se P aceitar R e depois for alcançada em A | **P** — a reclassificação só aparece no 69/2026, que não tem reserva. Nenhum Edital da amostra combina as duas regras. |
| 7 | TA / TR-posição | aceite em A | A: P. R: sem P | R chama o próximo | Não | **F** — caso estático. |
| 8 | SA / TR | aceite em R | R: P | A ainda tem P na fila | Latente | **P** — ver 9. |
| 9 | SA / TR (servida em R) | **aceite em A** (C7, Ícaro) | A: P. R: P, pela inclusão do aceite | — | **Sim**: P em duas vagas, e o próximo de R nunca é alcançado (cenários F e B2) | **I** — uma matrícula por pessoa no curso (10.4 e 10.5 vedam até cursos simultâneos). Se P **migra** para A, abrindo R ao próximo, ou se A a **pula**, é **P** — é a Q7 do estudo do 35. |
| 10 | SA / TR ou SR | desistência em R | R: sem P | **A ainda chama P** (cenário C) | Não há dupla, mas uma pessoa que desistiu do curso é convocada | **I** — "desista de realizar o curso". |
| 11 | SA / TR | inércia em R | R: sem P | A ainda chama P | como 10 | **I** forte — 11.3. |
| 12 | SA / TR ou SR | não atendimento em R | R: sem P | A ainda chama P | como 10 | **P** |
| 13 | SA / TR ou SR | **indeferimento em R, da autodeclaração ou do laudo** | R: sem P | A pode chamar P | Não | **F** — 8.10: "permanecendo apenas na lista de ampla". O 57 tem um conflito: o 8.11 dele manda a **eliminação do Processo** para o não comparecimento. É o único desfecho que o Edital limita a uma lista, e o GPS acerta **por acaso**, porque não distingue a causa. |
| 14 | SA / TR ou SR | indeferimento em R, por documentação geral | R: sem P | A pode chamar P | como 10 | **I** — 8.6: matrícula não efetivada. Mas o GPS não sabe distinguir 13 de 14. |
| 15 | SA / TR ou SR | reclassificação em R | R: P no fim | A chama P normalmente | Possível, como 9 | **P** |
| 16 | SA / SR | regularização em R | R: P. **A: P passa a ser chamável**, porque a habilitação é da Inscrição | A pode chamar P | Sim, se A chegar a P (B2) | **I** — como 9. |
| 17 | qualquer | chamada em aberto nas duas listas ao mesmo tempo | — | Nada impede a segunda convocação | Duas chamadas vigentes para a mesma matrícula | **P** — o Edital não proíbe, mas o candidato receberia duas convocações para o mesmo curso. |
| 18 | TA → sai de A | qualquer desfecho excludente em A, sob reversão por saldo já aplicada em R | A: recebeu a vaga cedida por R. R: 0 efetivas | A chama o próximo | Não. A vaga já mudou de lista, e P não volta a R porque R tem 0 vagas | **P** — DP-1 da 095. |
| 19 | TA → sai de A | qualquer desfecho excludente em A | R: apuração **vigente sem causa** | prévia e fila de R **mudam sem ato** em R | — | Fora do Edital. É disciplina do próprio sistema: FR-244 e FR-278a. |

**Leitura da matriz.**
- As linhas 2 a 5 e 9 a 12 concentram o risco.
- Nas linhas 2 a 5 o desfecho fica preso à ampla e a pessoa **volta** à reservada.
- Nas linhas 9 a 12 o desfecho fica preso à reservada e a pessoa **continua** na ampla.
- A linha 13 é a única em que o comportamento por lista é o que o Edital manda.
- A linha 9 é a única com dupla contagem confirmada nos dois Editais.

---

## 6. Fundamento

### 6.1 O que os Editais dizem

Os textos dos três Editais de pós-graduação (28, 35 e 57/2026) são praticamente iguais nas
cláusulas 4.3.1 e 8.7 a 8.12. Todos citam a Resolução CS nº 10/2017 do Ifes.

| Cláusula | O que manda | Alcance |
|---|---|---|
| 4.3.1 e 8.7 | Inscrito em vaga reservada concorre **concomitantemente** à reservada e à ampla; todos entram no sorteio da ampla | as duas listas |
| 8.8, 1ª frase | Sorteado dentro das vagas nas duas listas é classificado na **ampla** (§ 2º do art. 1º da Res. CS 10/2017) | posição no sorteio |
| 8.8, 2ª frase | Quem foi sorteado em vaga reservada e *"desista de realizar o curso"* tem a vaga preenchida pelo autodeclarado seguinte (§ 3º do art. 10) | **o curso** |
| 8.9 | Autodeclarado *"sorteado dentro do número de vagas"* da ampla não é computado na reservada e *"não constará na lista de classificados como autodeclarados"* | posição no sorteio, **não** a ocupação |
| 8.10 | Autodeclaração indeferida ou não comparecimento: desclassificado da PPI, *"permanecendo apenas na lista de ampla concorrência"* | **só a reservada** |
| 8.11 (só no 57) | Não comparecimento: *"perda do direito à reserva e na consequente eliminação do Processo Seletivo"* | **o certame**, e contradiz o 8.10 do mesmo Edital |
| 5.4 (57), laudo PcD | Laudo incompleto *"pode ocasionar a realocação do candidato como Ampla Concorrência"* | só a reservada |
| 8.3 e 8.6 (35) | Documentação incompleta: inscrição indeferida, *"a matrícula não será efetivada"*, vaga ao próximo habilitado | a pessoa, sem dizer a lista |
| 8.11 (28, 35) e 8.12 (57) | Desistentes antes ou depois do resultado: chamada de suplentes na ordem do sorteio | a ordem |
| 11.3 | Quem não acessa o AVA *"será considerado desistente e terá sua matrícula cancelada"* | **a matrícula**, que é uma só |
| 10.4 e 10.5 (35) | Vedada a matrícula simultânea em mais de um curso de especialização | entre cursos; dentro do mesmo curso, uma matrícula por natureza |

O 46/2026, de cursos técnicos sob a Lei 14.723/2023, usa o modelo **sequencial**: o cotista concorre
primeiro à ampla e só passa à reservada se não for alcançado nela. O princípio de que **a ampla
prevalece** é o mesmo, por outro caminho.

### 6.2 A desistência alcança a vaga, a lista ou o certame?

- **Desistência expressa: o curso (inferência forte).** O 8.8 diz "desista de realizar o curso". O
  objeto da desistência é o curso, e não a lista. Quem desistiu de realizar o curso não tem por que
  ser chamado pela outra lista do mesmo curso. **Mas o texto só trata da desistência em vaga
  reservada.** Ele não diz, com todas as letras, o que acontece com a ampla, nem com a reservada
  quando a desistência é na ampla.
- **Inércia: a matrícula (inferência forte).** "Considerado desistente e terá sua matrícula
  cancelada" fala de uma matrícula, que é uma só.
- **Indeferimento: depende da causa (texto explícito).**
  - Autodeclaração ou laudo: só a reservada (8.10; 5.4 do 57).
  - Documentação geral: a matrícula (8.6).
  - O 57 se contradiz no não comparecimento: o 8.10 manda permanecer na ampla, e o 8.11 manda eliminar.
- **Não atendimento: sem texto.** **Decisão institucional pendente.**
- **Reclassificação: sem texto.** O 69/2026, que a prevê, não tem reserva. **Decisão institucional
  pendente.**
- **Quem estava entre os titulares da ampla e sai dela.** O 8.9 fixa a exclusão pela **posição no
  sorteio** ("sorteados dentro do número de vagas"), e não pela ocupação. Lido ao pé da letra, a
  pessoa **não volta** à reservada, qualquer que seja o desfecho posterior. O GPS lê a ocupação. As
  duas leituras só divergem quando a ampla muda, e é exatamente o caso de Helena. **Decisão
  institucional pendente**, com inclinação textual para não voltar.
- **Quem aceitou a reservada e é alcançado pela ampla.** O 8.8 resolve o caso simultâneo ("dentro do
  número de vagas nas duas listas" → ampla). O caso sucessivo, em que a ampla chega depois, por
  suplência, não está escrito. Sob o princípio de que a ampla prevalece, a pessoa **migraria** para a
  ampla e liberaria a reservada ao próximo autodeclarado. Isso preserva a reserva para quem dela
  precisa. **Decisão institucional pendente** (é a Q7 do estudo do 35).

A Resolução CS nº 10/2017 **não foi lida**: não está entre os arquivos da amostra. Os Editais citam o
§ 2º do art. 1º e o § 3º do art. 10, e talvez a Resolução responda aos casos sucessivos.

---

## 7. Riscos

| Risco | Onde aparece | Gravidade |
|---|---|---|
| **Dupla ocupação**: uma pessoa conta em duas vagas, e o próximo autodeclarado nunca é alcançado | linhas 9 e 16; cenários F e B2 | **Alta.** Tira vaga de cotista, que é o que a ação afirmativa protege. É irreversível depois da matrícula. |
| **Convocar quem desistiu do curso** | linhas 2 a 5 e 10 a 12; cenários A e C | **Alta.** O candidato recebe "Você foi convocado" para um curso de que desistiu por escrito. A Administração pratica um ato append-only sem fundamento. |
| **Duas pessoas com aceite numa vaga reservada**, com o número em "1 ocupada" | cenário A | **Alta.** O teto da FR-253a esconde o conflito, e nenhuma tela o acusa. |
| **A proposta muda sem ato no recorte**, e a apuração continua "vigente" | linha 19 | Média. Contraria a disciplina da FR-278a, e quem conduz não sabe por que a PPI mudou. |
| **O indeferimento não distingue a causa** | linhas 13 e 14 | Média. O GPS acerta o 8.10 por coincidência e erra o 8.6 do mesmo jeito. |
| **Vaga reservada sem dono** quando todos os autodeclarados ocupam pela ampla | cenário D2; DP-2 | Média. Já registrada na 095 e no estudo do 35. |

---

## 8. Alternativas de regra

Cada alternativa é comparada pelos mesmos cinco critérios: aderência ao Edital, risco de dupla
ocupação, risco de vaga perdida, clareza para quem conduz, impacto nos dados gravados e esforço.

### 8.1 Mitigação sem código (vale já)

Antes de convocar numa lista, quem conduz confere se a pessoa tem desfecho ou aceite em outra lista
do mesmo Perfil. Se tiver, não convoca e registra o fundamento.

- Não muda nada no GPS.
- **Não protege o gesto "Convocar titulares"**, que confirma a lista inteira de uma vez. No caso de
  Helena, ele a convoca.
- No `gps_docs_demo` não há ato a rever (§4).

### 8.2 Comparação

| Alternativa | Aderência ao Edital | Dupla ocupação | Vaga perdida | Clareza | Dados gravados | Esforço |
|---|---|---|---|---|---|---|
| **A0 — Como está** | Fere o 8.8 ("desista de realizar o curso") e o 11.3; acerta o 8.10 por acaso | **Sim** (linhas 9 e 16) | Não | Baixa: a tela muda sem ato e o número esconde o conflito | Nenhum | Nenhum |
| **A1 — Cada lista é independente, mas a tela avisa.** A fila e a convocação marcam a pessoa com desfecho, aceite ou chamada em outra lista; "Convocar titulares" a mostra destacada e pede confirmação; a apuração reservada ganha uma causa de obsolescência para "a ampla mudou" | Igual à A0: a regra não muda, só fica visível | Continua possível, agora avisada | Não | **Alta** | Nenhum: só leitura e uma causa derivada | Baixo a médio |
| **A2 — O desfecho da pessoa alcança todas as listas dela no marco.** Desistência expressa e inércia, e, conforme a decisão, não atendimento e indeferimento por documentação geral, encerram a pessoa em todos os recortes do mesmo Perfil e marco. Reclassificação e indeferimento da autodeclaração ficam na lista | **Boa**: 8.8, 8.6, 8.10 e 11.3 | Resolve as linhas 2 a 5 e 10 a 12, mas **não** a 9 | Não | Alta: "desistiu" quer dizer desistiu do curso | O desfecho continua no recorte em que foi registrado; só a leitura passa a cruzar. Reservadas obsoletas pela nova causa precisam ser reemitidas | Médio: `_situacoes` e `ocupantes_da_ampla` passam a ler por pessoa |
| **A3 — A exclusão do 8.9 fica estática, pela posição no sorteio.** Quem foi sorteado dentro das vagas da ampla nunca entra na reservada, aconteça o que acontecer depois | **Literal** no 8.9; também resolve o Q1 do 35, o corte que propõe quem ocupa pela ampla | Resolve as linhas 2 a 6, mas **não** a 9 | Pode perder vaga: se a ampla publicar menos vagas do que o sorteio previa, ou receber reversão | Média: o "dentro do número de vagas" precisa de definição (publicadas? efetivas?) | Muda a apuração das reservadas onde a ampla mudou | Médio a alto: mexe na 016 e na 095/098, porque a prévia replica a conta |
| **A4 — Uma ocupação por pessoa no Perfil e marco, pulando.** A fila de qualquer recorte pula quem está servido ou tem chamada em aberto em outro recorte; a convocação recusa | Coerente com a matrícula única; **contraria** o princípio de que a ampla prevalece no caso sucessivo | **Resolve** as linhas 9, 16 e 17 | Não | Alta | Nenhum ato desfeito (FR-282); a recusa vale daqui em diante | Médio: uma recusa nova e a leitura cruzada |
| **A5 — Uma ocupação por pessoa, migrando para a ampla.** Alcançada pela ampla quem está servido numa reservada, a convocação pela ampla é oferecida como migração. O aceite produz, **no mesmo ato**, a exclusão na reservada, que chama o próximo autodeclarado | **A mais aderente ao 8.8** e à finalidade da reserva | Resolve 9 e 16 | Não | Média: um ato novo, que precisa de fundamento e de linguagem própria | Nenhum ato desfeito | **Alto**: um desfecho passa a gravar efeito em dois recortes, e a porta da 016 hoje grava um |

### 8.3 Recomendação

As alternativas se combinam: A1 é a camada de tela, A2 ou A3 tratam a pessoa que sai da ampla, e A4
ou A5 tratam a pessoa que aceita duas listas. A recomendação é:

1. **A2 para a desistência expressa e a inércia**, que têm texto. O não atendimento e o indeferimento
   por documentação geral entram se as QC3 e QC4 responderem "a pessoa". A2 resolve o caso de Helena
   sem mexer no corte nem na prévia, e casa com o significado que o Edital dá à palavra "desistir".
2. **A4 agora, como trava mínima contra a dupla ocupação.** Se a QC7 decidir pela migração, A5 vem
   depois. A4 é a forma mais barata de garantir a invariante "uma Inscrição ocupa no máximo um recorte
   do Perfil e marco". A5 é a mais fiel ao Edital, mas é um ato novo e precisa de decisão.
3. **A1 em qualquer caso**, por duas razões que valem para toda alternativa: a causa de
   obsolescência para "a ampla mudou" (FR-244 e FR-278a) e o fim do teto silencioso, com "ocupadas"
   acusando conflito quando houver duas pessoas numa vaga.
4. **A3 só se o usuário quiser ler o 8.9 ao pé da letra** e resolver junto o Q1 do estudo do 35. Ela
   não substitui A4 nem A5.

---

## 9. Perguntas ao usuário

1. **QC1.** A **desistência expressa** registrada numa lista alcança só aquela vaga, só aquela lista,
   ou a pessoa no certame, isto é, todas as listas dela no mesmo Perfil e marco? *Recomendação: a
   pessoa no certame. O 8.8 fala em "desista de realizar o curso".*
2. **QC2.** O **cancelamento por inércia** (11.3, "considerado desistente") segue a mesma resposta da
   QC1? *Recomendação: sim.*
3. **QC3.** O **não atendimento** à convocação numa lista encerra a pessoa nas outras? Não há texto.
   *Recomendação: sim, porque a convocação é para a matrícula no curso. A decisão é institucional.*
4. **QC4.** O **indeferimento** deve registrar a causa e ter alcance diferente para cada uma?
   - condição de cotista (autodeclaração, heteroidentificação, laudo): só a reservada, como diz o 8.10;
   - documentação geral: todas as listas, como diz o 8.6.

   E qual cláusula vale no 57, o 8.10 (permanece na ampla) ou o 8.11 (eliminação do Processo)?
5. **QC5.** A **reclassificação** (fim da fila) fica só na lista em que foi registrada? *Recomendação:
   sim, porque é ato de posição. Nenhum Edital da amostra combina reclassificação e reserva.*
6. **QC6.** Quem estava entre os titulares da ampla e **sai dela** volta a concorrer na reservada?
   *Recomendação: não. O 8.9 fixa a exclusão pela posição no sorteio. Com QC1 = "a pessoa no
   certame", a pergunta só sobra para a reclassificação e para o titular eliminado na Etapa.*
7. **QC7** (a Q7 do estudo do 35). Quem **já aceitou ou regularizou numa reservada** e é alcançado pela
   fila da ampla: a ampla o **pula**, ou o **migra**, abrindo a reservada ao próximo autodeclarado?
   E isso muda depois da homologação da matrícula? *Recomendação: decidir com o setor. Pular é o
   mínimo seguro; migrar é o mais fiel ao 8.8.*
8. **QC8.** A mesma pessoa pode ter **chamada em aberto em duas listas** ao mesmo tempo?
   *Recomendação: não. Uma chamada vigente por pessoa no Perfil e marco.*
9. **QC9** (amplia a Q8 do estudo do 35). "Ocupadas" deve contar **pessoas distintas** e acusar
   conflito, em vez de saturar no teto? *Recomendação: sim.*
10. **QC10.** A regra nova vale **só daqui em diante**, ou o acervo deve ser revisto? *Recomendação:
    daqui em diante, mais o inventário da §4 rodado na VM de testes antes da spec. Produção ainda não
    existe, pela D-013 da 115.*
11. **QC11.** O setor pode confirmar a leitura, ou trazer o texto da **Resolução CS nº 10/2017**
    (§ 2º do art. 1º e § 3º do art. 10)? Ela pode responder a QC6 e a QC7.
12. **QC12.** Quer o caminho da §8.3 (A2, A4 e A1, com A5 depois de decidida a QC7) como escopo de uma
    spec, ou prefere outra combinação?

---

## 10. Escopo mínimo de uma spec futura

A spec depende das respostas às QC1 a QC8. O escopo abaixo supõe a recomendação da §8.3.

**Entra:**
- **Alcance do desfecho, por espécie e por causa**:
  - uma tabela declarada, ao lado de `EFEITO_POR_DESFECHO`, que diga se o desfecho é "da pessoa no
    marco" ou "da lista";
  - a leitura de "encerrados" e de "quem ocupa pela ampla" passa a ser por pessoa, para as espécies
    "da pessoa";
  - sem tabela nova de vínculo e sem reescrever ato.
- **Invariante de uma ocupação por pessoa no Perfil e marco**:
  - a fila de qualquer recorte pula quem está servido ou em aberto em outro recorte;
  - a convocação recusa com um código novo, que nomeia a outra lista;
  - "Convocar titulares" não alcança essa pessoa.
- **Obsolescência cruzada**:
  - a apuração reservada congela, no universo, quem ocupava a ampla (um id por inscrição);
  - uma sétima causa, "a ocupação da ampla mudou", torna a reservada obsoleta;
  - a `apuracao_seguinte` do desfecho na ampla não reemite a reservada sozinha; ela aparece obsoleta,
    como pede a FR-263.
- **"Ocupadas" sem teto silencioso**: duas pessoas numa vaga viram conflito declarado na tela da
  ocupação e na convocação, e não `min(2, 1)`.
- **Aviso na tela**: o cartão da pessoa na convocação diz o desfecho, ou o aceite, que ela tem em
  outra lista, com a data.
- **Inventário e decisão do acervo** (QC10).
- **Testes**: cada linha da matriz da §5 que mudar de comportamento vira um caso de integração, com
  os dois recortes lidos. Hoje não há nenhum.

**Fica fora**, e cada item tem dono próprio:
- o corte da reservada que propõe quem ocupa pela ampla: Q1 do estudo do 35 e DP-1 da 095;
- a reversão quando todos os autodeclarados ocupam pela ampla: Q4 do estudo do 35 e DP-2 da 095;
- a migração da QC7, se decidida, porque é um ato novo e merece incremento próprio;
- o registro da causa do indeferimento (QC4): pode ser a mesma spec, se a decisão vier junto;
- documentos da convocação, "não se aplica", formalização e UX da composição.

**A prévia da 095 e da 098** não simula desfechos. Por isso o alcance do desfecho não muda a
equivalência dela (FR-2340). Só a A3 mexeria nas duas.

---

## Apêndice — reprodução

- `reproducao/estado.py`: lê o estado de cada recorte de um Edital (apuração vigente e causas, ordem,
  quem ocupa pela ampla, convocações, titulares, ocupantes e fila recalculados, e a prévia do gesto),
  sem gravar nada.
- `reproducao/simular.py`: os cenários A, B2, C, C2 e D2, pelos comandos de domínio. Desliga **só** a
  guarda documental do aceite, no próprio processo.
- `reproducao/inventario.sql`: pessoas com convocação vigente em mais de um recorte do mesmo Edital,
  Perfil e marco. Só leitura.
- `reproducao/saida.txt`: a saída dos cenários, sem o corpo dos e-mails.

Para repetir: clone o banco de demonstração, migre a cópia para a `main` e rode cada cenário num clone
próprio.

```bash
createdb -T gps_docs_demo conc_estudo
```

```bash
cd backend && make provisionar migrate provisionar DB_NAME=conc_estudo POSTGRES_DB=conc_estudo
```

```bash
createdb -T conc_estudo conc_a
```

```bash
cd backend && DB_NAME=conc_a uv run python manage.py shell -c "exec(open('../doc/estudo-concorrencia-concomitante-2026-11-07/reproducao/simular.py').read()); cenario_a(); exec(open('../doc/estudo-concorrencia-concomitante-2026-11-07/reproducao/estado.py').read()); mostrar('93')"
```

O `.env` do backend precisa estar carregado no ambiente, como em qualquer `manage.py` chamado à mão.
