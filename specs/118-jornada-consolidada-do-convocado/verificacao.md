# Verificação: A jornada consolidada do candidato convocado (118)

**Data**: 2026-11-04 · **Base**: `main` em `38ea4ff9` (com o #380 e o #381) · **Branch**:
`claude/busy-hofstadter-5f006e`

## Linha de base e totais da suíte (T002, T033)

| | Commit | Passando | Pulados | Falhas | Tempo |
|---|---|---|---|---|---|
| Antes | `38ea4ff9` (`main`) | 15451 | 12 | 0 | 808 s |
| Depois | esta branch | 15751 | 12 | 0 | 716 s |

As duas com `make test-pg` (4 workers, `worksteal`), os grupos `assistente` e `navegador`
instalados e banco próprio (`ps_118_base`, `ps_118_impl`). A linha de base rodou numa worktree
separada no commit da `main`, para que nada editado aqui a falseasse. Os doze pulados são os doze
do `CLAUDE.md`: dez do vocabulário da composição, a recusa por vendor e o E2E da Caixa — conferidos
lista a lista (`-rs`, agrupados por arquivo e motivo), e iguais nas duas rodadas. Os 300 casos a
mais são os desta feature: a projeção, a ação da situação, a jornada nas telas e no navegador.

`make lint` (os dois passos) e `make check` verdes; `makemigrations --check`: *"No changes
detected"*. Nenhuma migration, rota, comando ou tabela (FR-3756), e o provisionamento continua
protegendo 53 tabelas append-only.

## Como os cenários foram percorridos

Pelas *fixtures*, como o roteiro do #375 pedia — agora em `tests/fixtures/jornada_do_convocado.py`,
um cenário por certame, com as letras do plano. Cada um foi aberto num Chromium de verdade
(`tests/navegador/test_jornada_consolidada_do_convocado.py`), a 375 × 812 e a 1280 × 900: o
acompanhamento, a convocação e, quando há, o Requerimento. Em todas as 22 combinações e nas duas
larguras: **sem rolagem horizontal, sem violação da política de conteúdo no console e sem nome
acessível repetido** entre os botões de envio e os rótulos de escolher arquivo. Em A, C1, C2, F e J,
a 375 px, a frase do bloco *O que fazer agora* e o primeiro link de tarefa terminam dentro dos
812 px da primeira tela (SC-1119).

**Pelo teclado, em F a 375 px** (SC-1122): o Tab percorre o cabeçalho e depois o conteúdo sempre
para baixo — as duas âncoras do bloco 1, *"Ver e corrigir os documentos pendentes"*, *"Ver o
arquivo recebido: Histórico escolar do ensino médio"*, *"Enviar outro arquivo: Histórico…"*, o
campo, *"Enviar: Histórico escolar do ensino médio"*, o campo e *"Enviar: Comprovante de
residência"*, os arquivos conferidos, *"Conferir o Requerimento de Matrícula enviado"* e *"Voltar ao
acompanhamento"* —, com contorno visível em todo foco. Ativar a âncora do pendente leva o foco ao
cartão dele, que tem o selo *"Precisa de correção"*.

**As capturas** estão em [`capturas/`](capturas/): `antes/` foi tirada na linha de base, com a mesma
fixture e o mesmo roteiro; `depois/`, nesta branch. A 375 px, o acompanhamento e a convocação de
todos os cenários; o Requerimento onde ele é o ponto (C2, G, M, M0, N, N0, G0); e a convocação em
desktop de F e G. Em JPG, como as do #375, para caber em 6,3 MB.

## As quatro perguntas, por cenário (SC-1124)

Texto literal das telas a 375 px, de `depois/`. Os horários são os da execução que gerou as
capturas. **P1** — *preciso enviar mais alguma coisa?* **P2** — *o que está com a comissão?*
**P3** — *qual é o prazo?* **P4** — *o que acontece depois?*

### A — documentos sem Requerimento

- **P1**: *"Você ainda precisa enviar 4 documentos."*, com as quatro âncoras e *"Ver os documentos
  que faltam"*; cada cartão diz *"Falta enviar."*
- **P2**: nada; não há bloco *O que você já apresentou*.
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*, igual nas duas telas.
- **P4**: *"Se você não atender no prazo, a comissão poderá registrar o não atendimento desta
  convocação."*

### B — Requerimento sem documentos, a preencher (sem regressão)

- **P1**: *"Preencher o Requerimento de Matrícula."* com o link direto a ele, como hoje.
- **P2**: nada.
- **P3**: no acompanhamento, *"Prazo desta convocação: até 09/11/2026, às 18h18."*; na convocação, o
  mesmo instante entre os dados; e agora também na página do Requerimento (FR-3753).
- **P4**: a mesma frase de consequência.

### B2 — Requerimento sem documentos, já enviado (sem regressão)

- **P1**: *"Seu Requerimento de Matrícula foi enviado."*, ação principal, como hoje (D-017).
- **P2**: nada no portal; o Requerimento: *"Enviado não é alterado. Se algo mudou, a atualização
  cria uma nova versão, e esta continua registrada."* (FR-3752).
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*
- **P4**: a frase de consequência.

### C1 — os dois, nada enviado

- **P1**: *"Você ainda precisa enviar 4 documentos e preencher o Requerimento de Matrícula."* O link
  principal é *"Ver o que falta na convocação"*, e não mais o Requerimento; na convocação, o
  Requerimento é a última tarefa da lista.
- **P2**: nada.
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*
- **P4**: a frase de consequência.

### C2 — os dois, só o Requerimento enviado (a falsa conclusão)

- **P1**: *"Você ainda precisa enviar 4 documentos."*, *"Ver o que falta na convocação"*. **Antes**,
  a mesma tela dizia *"Seu Requerimento de Matrícula foi enviado."* com o botão para conferi-lo
  (`antes/C2-acompanhamento-375.jpg`).
- **P2**: *"✓ Requerimento de Matrícula enviado. Conferir o Requerimento de Matrícula enviado"*,
  abaixo da ação principal, e no bloco *O que você já apresentou*.
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*
- **P4**: a frase de consequência.

### D — o certificado aproveitado da inscrição

- **P1**: *"Nada por enquanto. Você não tem mais documentos para enviar agora. A comissão ainda vai
  concluir a análise."*
- **P2**: *"Com a comissão: 1 documento."*; o cartão, com o selo *"Aguardando conferência"*: *"Você
  já enviou este documento na inscrição, em 04/11/2026. Não precisa enviar de novo. A comissão vai
  conferir."* Nenhum "atendido".
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*
- **P4**: *"A comissão ainda vai concluir a análise."* e a frase de consequência.

### E — os quatro enviados, aguardando

- **P1**: *"Nada por enquanto. Você não tem mais documentos para enviar agora. A comissão ainda vai
  concluir a análise."* **Antes**: *"Siga as instruções do Edital para esta convocação."*, que
  induzia uma ação inexistente.
- **P2**: *"Com a comissão: 4 documentos."*; cada um: *"Recebido em 04/11/2026, às 18h18. A comissão
  vai conferir; você não precisa fazer nada agora."*
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*
- **P4**: a comissão conclui a análise; a frase de consequência.

### F — um pendente e um a enviar, com o prazo em curso

- **P1**: *"Você ainda precisa corrigir 1 documento e enviar 1 documento."*; na convocação, primeiro
  *"Histórico escolar do ensino médio — Falta a página 2."*, depois *"Comprovante de residência"*, e
  *"Ver e corrigir os documentos pendentes"*. O cartão do histórico tem o fundo de aviso e o selo
  *"Precisa de correção"*: *"Precisa de correção: Falta a página 2. Envie um novo arquivo até
  09/11/2026, às 18h18."*
- **P2**: os dois conferidos, com *"Conferido: de acordo com o Edital."*; o Requerimento enviado.
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*, o mesmo no cartão.
- **P4**: a frase de consequência.

### G — o pendente com o prazo vencido, o Requerimento nunca enviado

- **P1**: não. *"O prazo terminou em 04/11/2026, às 18h19. O fim do prazo não decide nada sozinho:
  quem registra o resultado é a comissão. Não é mais possível enviar documentos nem o Requerimento
  de Matrícula pelo portal."*; nenhum formulário.
- **P2**: o resumo *"Até o prazo, ficou assim"*: *"Sem envio: Histórico escolar do ensino médio
  (correção pedida), Certidão de nascimento ou casamento, Certificado de conclusão do ensino médio e
  Comprovante de residência."* e *"Requerimento de Matrícula: não enviado até o prazo. Não é mais
  possível enviá-lo pelo portal."*
- **P3**: *"O prazo desta convocação terminou em 04/11/2026, às 18h19."*
- **P4**: *"quem registra o resultado é a comissão"*. A página do Requerimento diz *"O prazo
  terminou"*, o mesmo núcleo e *"Voltar à convocação"* — **antes**, a recusa genérica *"Operação
  incompatível com a situação atual"* e *"A comissão vai decidir."* (`antes/G-requerimento-375.jpg`),
  e nenhum rascunho nasce.

### H — tudo conferido, sem desfecho

- **P1**: *"Nada por enquanto. Você não tem mais documentos para enviar agora. A comissão ainda vai
  concluir a análise."*
- **P2**: os quatro *"Conferido: de acordo com o Edital."* e o Requerimento enviado; nenhum
  "Conforme" sozinho, nenhum "tudo certo".
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*
- **P4**: a comissão conclui a análise.

### I1 — o aceite

- **P1**: *"Nada por enquanto."*
- **P2**: a lista *"O que você enviou nesta convocação"*, só de histórico.
- **P3**: nenhum, e nenhum formulário.
- **P4**: *"Vaga aceita"* nas duas telas e *"Este registro não é matrícula, bolsa nem contrato: ele
  registra o resultado desta convocação. Os próximos passos são os que o Edital indica."* O
  Requerimento: *"Enviado não é alterado."*

### I2 — o indeferimento com itens não enviados

- **P1**: *"Nada por enquanto."*, *"Ver o que você enviou nesta convocação"*.
- **P2**: *"Enviado em 04/11/2026; não foi conferido antes do resultado."*, *"Precisava de correção:
  Falta a página 2."* e dois *"Não enviado."*
- **P3**: nenhum.
- **P4**: *"Resultado registrado"*, *"Indeferido na convocação"*, com o fundamento e a data.

### J — a pendência sobre item que nunca recebeu arquivo

- **P1**: *"Você ainda precisa enviar 1 documento."*; o cartão: *"Precisa de correção: Envie conta de
  água, luz ou telefone dos últimos 3 meses. Envie o arquivo até 09/11/2026, às 18h18."* — e não
  "outro arquivo".
- **P2**: *"Com a comissão: 3 documentos."*
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*
- **P4**: a frase de consequência.

### K — a comunicação ainda não enviada

- **P1**: *"Você ainda precisa enviar 4 documentos e preencher o Requerimento de Matrícula."*
- **P2**: nada.
- **P3**: *"O prazo ainda não começou a correr: ele conta a partir do envio da comunicação. Você já
  pode enviar."* A data só aparece em *Sobre esta convocação*, como *"Vencimento registrado"*.
  **Antes**, a lista dizia *"Envie até …"* com a data de um prazo que não corria (F12).
- **P4**: o prazo começa com a comunicação; nenhuma consequência enquanto ele não corre.

### L — só um facultativo sem envio

- **P1**: *"Nada por enquanto. Você não tem mais documentos para enviar agora. A comissão ainda vai
  concluir a análise."* e *"Se quiser, você ainda pode enviar o documento opcional até 09/11/2026,
  às 18h18."*; o bloco *Documentos opcionais* tem o envio, e *"Há documento opcional que você pode
  enviar, se quiser."* leva a ele.
- **P2**: *"Com a comissão: 2 documentos."* — o opcional não entra na conta.
- **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."*
- **P4**: a comissão conclui a análise.

### M — o Processo encerrado, a chamada em aberto, o prazo correndo

- **P1**: não. *"O envio pelo portal está encerrado"*: *"Este Processo Seletivo foi encerrado, e não
  é mais possível enviar documentos nem o Requerimento de Matrícula pelo portal."*; nenhum
  formulário de documento nem chamado ao Requerimento.
- **P2**: *"Recebido em 04/11/2026, às 18h18; não foi conferido antes do encerramento do Processo."*,
  com o selo *"Não conferido"*; e *"Requerimento de Matrícula: não enviado. O envio pelo portal está
  encerrado."*
- **P3**: nenhuma frase diz que o prazo venceu; a data fica nos dados do ato.
- **P4**: *"Se você enviou algo que não aparece aqui, fale com o atendimento."* Nenhuma promessa de
  conferência ou resultado.

### N — o indeferimento, com o Requerimento pedido e nunca enviado

- **P1**: *"Nada por enquanto."*
- **P2**: *"Requerimento de Matrícula: não enviado."* — e não "não pedido".
- **P3**: nenhum.
- **P4**: *"Resultado registrado"*, *"Indeferido na convocação"*. A página do Requerimento: *"Requerimento
  de Matrícula não enviado"*, *"Esta convocação já tem resultado registrado, e o Requerimento não foi
  enviado. Não é mais possível enviá-lo pelo portal."* — **antes**, *"Ainda não é a hora"* e
  *"quando você for convocado"* (`antes/N-requerimento-375.jpg`), com e sem rascunho.

### K2 — o prazo não iniciado, com um pendente, uma tarefa e um opcional

- **P1**: *"Você ainda precisa corrigir 1 documento e enviar 1 documento."*; os cartões dizem
  *"Precisa de correção: Falta a página 2. Envie um novo arquivo."* e *"Opcional: envie se quiser."*
  — nenhum com *"até ‹data›"*.
- **P2**: nada.
- **P3**: *"O prazo ainda não começou a correr: ele conta a partir do envio da comunicação. Você já
  pode enviar."*
- **P4**: o prazo começa com a comunicação.

### G0 — sem documento, o Requerimento não enviado, o prazo vencido

- **P1**: a ação de hoje, *"Siga as instruções do Edital para esta convocação."*, e a linha sem link
  *"Requerimento de Matrícula: não enviado até o prazo. Não é mais possível enviá-lo pelo portal."*
- **P2**: nada.
- **P3**: *"O prazo terminou em 04/11/2026, às 18h20. O fim do prazo não decide nada sozinho: quem
  registra o resultado é a comissão."*; nos dados, *"Vencimento registrado"*.
- **P4**: quem registra o resultado é a comissão.

### N0 — sem documento, o Requerimento não enviado, o resultado registrado

- **P1**: *"Nada por enquanto."* e *"Requerimento de Matrícula: não enviado."*
- **P2**: nada.
- **P3**: nenhum; nos dados, *"Vencimento registrado"*.
- **P4**: *"Resultado registrado: Indeferido na convocação — …"*; a página do Requerimento diz *"não
  enviado"*.

### M0 — sem documento, o Processo encerrado, o Requerimento não enviado

- **P1**: *"Siga as instruções do Edital para esta convocação."* e *"Requerimento de Matrícula: não
  enviado. O envio pelo portal está encerrado."*, sem *"Preencher"*.
- **P2**: nada.
- **P3**: nenhum prazo e nenhuma consequência no topo (ver *Decisões de implementação*); nos dados,
  *"Vencimento registrado"*.
- **P4**: a página do Requerimento diz *"O envio pelo portal está encerrado"*, sem formulário, e o
  GET não cria rascunho.

### Controle — Edital sem documento e sem Requerimento

- **P1**: *"Siga as instruções do Edital para esta convocação."*, *"Ver convocação"*, como hoje.
- **P2**: nada. **P3**: *"Prazo desta convocação: até 09/11/2026, às 18h18."* **P4**: a frase de
  consequência.

## O caminho de leitura (FR-3734, FR-3756, SC-1125, SC-1127, SC-1128)

**Nada gravado.** Antes e depois de um GET de cada tela em C2, G e M, todas as tabelas do banco
foram contadas: só a trilha (`RegistroAuditoria`) ganhou a linha da leitura da convocação. Em G, M
e N, com e sem rascunho, o GET do Requerimento não cria rascunho (em M0, o teste do #381 já o
prova); em G0, N0 e M0, os GET do acompanhamento e da convocação gravam só aquela linha.

**A mesma recusa.** A inscrição alheia e a inexistente recebem 404 com o mesmo corpo nas três telas
(salvo a correlação e o token de CSRF de cada resposta), e a página do Requerimento continua com
`Cache-Control: no-store`.

**Consultas**, medidas com um teste descartável rodado na linha de base e nesta branch, sobre os
mesmos cenários:

| Cenário | Acompanhamento, antes → depois | Convocação, antes → depois |
|---|---|---|
| sem convocação | 17 → 17 | — |
| sem documento nem Requerimento | 20 → 21 | 20 → 19 |
| B, B2, G0, M0 | 25 → 26 | 25 → 24 |
| N0 | 23 → 24 | 23 → 22 |

E com documento, a mesma chamada com um e com seis itens custa o mesmo nas duas telas
(`test_as_duas_telas_custam_o_mesmo_com_um_e_com_seis_itens`). A linha informativa não acrescenta
consulta: G0 antes do prazo, sem a linha, e depois, com ela, custa o mesmo
(`test_a_linha_informativa_nao_acrescenta_consulta`).

**Divergência registrada, para decisão.** A SC-1128 pede que, em G0, N0 e M0, *"o número de
consultas das duas telas é o mesmo de antes"*. A convocação cumpre (uma a menos), mas o
acompanhamento com convocação paga **uma** consulta a mais em toda chamada sem documento — a da lista
da chamada, que é como a tela sabe que não há documento. É o custo que a FR-3734 admite (*"com
convocação, um número fixo"*), e o mesmo em B, B2 e no Edital sem nada. A primeira versão pagava
duas; a segunda saiu ao usar a convocação vigente que o seletor da `019` já lê, em vez de reler a
cadeia. Zerar a que sobra pediria saber dos documentos pelo conteúdo do Edital, e uma Retificação que
tirasse o documento depois da convocação esconderia itens gravados na chamada.

## Decisões de implementação que a spec não fixava

- **Selos fechada a chamada.** *"Precisa de correção"* vira *"Precisava de correção"*, e o que estava
  com a comissão ganha *"Não conferido"* com o Processo encerrado ou o resultado registrado:
  *"Aguardando conferência"* prometeria uma conferência que o sistema recusa (FR-3724, SC-1120).
- **O bloco 3 encerrada a chamada** chama-se *"O que ficou sem envio"*: *"O que falta"* depois do
  prazo convidaria a enviar.
- **O bloco *Prazo*** aparece com a chamada aberta e encerrada pelo prazo (*"O prazo desta convocação
  terminou em …"*). Com o Processo encerrado ou com resultado ele sai: falar do prazo ali diria que
  ele ainda importa.
- **Sem documento, a data só é prazo enquanto corre.** Com a comunicação ainda não enviada, o prazo
  vencido, o resultado registrado ou o Processo encerrado, os dados dizem *"Vencimento registrado"*,
  e *"dentro do prazo acima"* sai. Em M0, o acompanhamento também não mostra o prazo nem a
  consequência: com o Processo encerrado ninguém registra não atendimento (D-015, D-020).
- **"Sem envio" no resumo** inclui o pendente com apresentação anterior, marcado *"(correção
  pedida)"*: o novo arquivo não chegou.
- **O Requerimento não enviado** aparece no resumo do bloco 1 (encerrada) e na lista do histórico
  (decidida), e nunca sob *"O que você já apresentou"*.
- **O modelo anexo** continua para baixar até o resultado.

## Expectativas de teste alteradas, por cenário (SC-1123, T032)

Cada mudança troca o texto que saiu da spec pelo que entrou, e mantém a garantia de antes.

| Arquivo | Teste | Cenário | Saiu → entrou | A garantia de antes |
|---|---|---|---|---|
| `unit/portal/test_situacao_da_inscricao.py` | `test_vencimento_decorrido_sem_desfecho_continua_convocado` | vencido sem desfecho | *"ainda não foi registrado"* → o núcleo da FR-3748 | "Convocado", "terminou em", nenhuma perda nem consequência |
| `interface/test_portal_caminho_da_convocacao.py` | `test_a_secao_mostra_a_chamada_o_prazo_e_o_caminho` | aberta | `DD/MM/AAAA HH:MM` → `DD/MM/AAAA, às HHhMM` | a data, "contado do envio", o caminho |
| idem | `test_antes_do_envio_diz_que_o_prazo_nao_comecou` | K | *"ainda não foi enviada"* → *"conta a partir do envio da comunicação"* | "não começou a correr", nenhuma consequência |
| idem | `test_vencimento_decorrido_nao_decide_nada_sozinho` | G sem documento | *"ainda não foi registrado"* → *"não decide nada sozinho: quem registra o resultado é a comissão"* | idem ao primeiro |
| idem | `test_a_sucessora_ocupa_o_lugar_da_sucedida` | sucessão | formato | a sucessora aparece, a sucedida não (também pela data sem hora) |
| `interface/test_portal_convocacao.py` | `test_a_tela_mostra_a_chamada_o_prazo_e_o_que_fazer` | aberta sem documento | formato | a data e "O que fazer" |
| idem | `test_antes_do_envio_a_tela_diz_que_o_prazo_nao_comecou` | K sem documento | *"prazo não começou a correr"* → *"prazo ainda não começou a correr"* | o mesmo aviso |
| `interface/test_portal_documentos_da_convocacao.py` | `test_a_convocada_ve_o_que_apresentar_e_ate_quando` | K | *"Documentos pedidos nesta convocação"* e *"Envie até"* → os blocos e a frase do prazo não iniciado | quatro *"Falta enviar"*, instrução, nenhum item da inscrição |
| idem | `test_a_convocada_envia_pelo_portal_e_le_o_resultado` | E, F | *"aguardando conferência"* e *"Pendente: …"* → o selo, *"A comissão vai conferir; você não precisa fazer nada agora."* e *"Precisa de correção: … Envie um novo arquivo"* | o motivo sem quem conferiu; nenhum termo de vínculo |
| idem | `test_depois_do_vencimento_a_tela_diz_o_prazo_e_nao_oferece_envio` | G | *"A comissão vai decidir."* → o núcleo | "O prazo terminou em", nenhum formulário |
| idem | `test_o_certificado_da_inscricao_aparece_atendido` | D | *"Atendido pelo documento…"* → *"Você já enviou este documento na inscrição, em …"* | nenhum envio; a referência é uma só |
| idem | `test_a_pendencia_sobre_o_que_nao_chegou_mostra_o_motivo` | J | *"Pendente: …"* → *"Precisa de correção: … Envie o arquivo"* | o motivo aparece |
| idem | `test_sem_documento_na_convocacao_a_tela_e_a_de_antes` | sem documento | a ausência do cabeçalho antigo, que agora passaria vazia → a ausência dos blocos e a presença de "O que fazer" | a estrutura de antes |
| `integration/requerimentos/test_prazo_da_chamada.py` | `test_depois_do_vencimento_o_requerimento_nao_se_abre_nem_se_envia` | G | *"A comissão vai decidir"* → o núcleo, igual na tela e na recusa | a recusa, o código, nada aberto |
| `integration/convocacao/test_documentos_da_convocacao.py` | `test_depois_do_vencimento_a_apresentacao_e_recusada_e_nada_e_gravado` | G | idem, e a frase igual à de `frase_do_prazo_decorrido` | a recusa, nada gravado |
| `navegador/test_jornada_dos_documentos_da_convocacao.py` | três jornadas | A, F, D, G | o título da lista, *"Pendente: …"*, *"Atendido…"*, *"A comissão vai decidir."* → os textos novos | quatro *"Falta enviar"*, o motivo, o aproveitamento sem reenvio, nenhum envio depois do prazo |
| `test_vocabulario_*.py` (três) | as listas literais | — | `_documentos_da_convocacao.html`, que saiu → os três parciais novos, `portal/obrigacoes.py` e `portal/situacao.py` | a varredura alcança tudo o que o portal diz |

**Os textos que saem**, procurados em `tests/` e no portal: *"Atendido pelo documento"* só resta em
`test_permissoes_dos_documentos_da_convocacao.py`, sobre a **gestão** (*"…da inscrição"*), que a
FR-3758 mantém; *"aguardando conferência"* só nos testes que provam a ausência e nas telas da
gestão; *"Pendente: "*, *"Envie outro arquivo"*, *"Envie até "*, *"O prazo informado nesta
convocação já passou"* e *"Situação registrada: "* não restam; *"A comissão vai decidir"* só onde se
prova que saiu; *"Prazo para atender"* só na **mensagem** de convocação (`convocacao/application/
comunicar.py`, FR-290 da `019`, fora desta spec como X3); *"Se algo mudar e você for convocado"* só
para quem não tem convocação. **Os que ficam** continuam presos: *"Falta enviar."*
(`test_a_convocada_ve_o_que_apresentar_e_ate_quando`), *"Não se aplica: "* (`ob`), *"Conferir o
Requerimento de Matrícula enviado"*, *"Seu Requerimento de Matrícula foi enviado."* e *"Siga as
instruções do Edital para esta convocação."* (`jc::test_b_e_b2_sem_documento_ficam_como_hoje`,
`::test_sem_documento_e_sem_requerimento_a_instrucao_neutra`) e *"não decide nada sozinho"*.

## Fora desta entrega

Como o pedido delimitou: o aviso por e-mail (QI-7), a correção da convocação por sucessão na gestão,
qualquer regra de prazo, "Minhas inscrições" (X1) e a mensagem de convocação (X3). A recusa do
Requerimento com o Processo encerrado no comando, que a spec deixava para PR próprio, já estava na
`main` (#381) quando esta implementação começou; a `118` só lê a política que ele deixou.
