# Research: Relatório consolidado da unidade

Decisões técnicas do plano, cada uma com a razão e a alternativa descartada. A base é o estudo de
24/10/2026 ([`doc/estudo-relatorio-consolidado-de-gestao-2026-10-24.md`](../../doc/estudo-relatorio-consolidado-de-gestao-2026-10-24.md))
e o código da `099` como mergeado em `50badd38`.

## R-001 — A `099` se separa em fatos e redação, e a prova é a composição idêntica

- **Decision**: `relatorio_do_edital.fatos_do_edital(edital, *, agora)` faz as leituras e aplica as
  regras: números por Perfil, pendências como `Pendencia(tipo, perfil_id, quantidade, marco, ate)`,
  espécie, registros posteriores, contagens. `montar` passa a chamar `fatos_do_edital`, fazer as
  leituras que só o documento individual usa (cronograma, datas, documentos, Retificações por
  extenso, série diária) e redigir. As frases de pendência saem de uma função que recebe os tipos.
- **Rationale**: a FR-2547 da `099` proíbe decidir situação lendo texto, e somar pendências redigidas
  seria isso (D-002). A separação também barateia o consolidado, que não precisa do anexo de cada
  Edital.
- **Prova**: antes da refatoração, a composição do PDF individual (`relatorio_pdf.composicao`, todos os
  itens com fonte, corpo, posição e texto) foi serializada nos quatro estados do cenário coerente —
  pendente, sem pendência, aberto, cancelado —, com os resumos SHA-256 dos documentos fixados e os
  UUIDs normalizados, porque cada montagem do cenário sorteia identificadores. Duas montagens
  independentes deram o mesmo resumo da serialização. A mesma comparação, depois da refatoração, é a
  SC-940. Os bytes do PDF não servem de prova entre montagens: o endereço de cada resultado leva o
  UUID da publicação.

  Linha de base, em `50badd38` (24/10/2026):

  | Estado | Resumo da composição normalizada | Caracteres |
  |---|---|---|
  | pendente | `e6df6298a6c53630…` | 45471 |
  | sem-pendencia | `d351b9a7f98a763f…` | 43483 |
  | aberto | `609d761b7ee39ea7…` | 28702 |
  | cancelado | `5e4d77c8c44ebd4c…` | 32343 |
- **Alternatives considered**: o consolidado reimplementar as pendências com consultas em lote —
  segunda verdade, recusada pela FR-2569; ler as frases — recusada pela FR-2547 da `099`.

## R-002 — O consolidado é `map` de fatos e `reduce` puro

- **Decision**: `relatorio_consolidado.ler(conjunto, *, agora)` abre `leitura_consistente()` da `099`,
  chama `fatos_do_edital` para cada Edital incluído e entrega a lista a `consolidar(fatos, conjunto,
  agora)`, que não toca o banco. Página e PDF leem o mesmo `Consolidado`.
- **Rationale**: a soma pura testa-se com fatos sintéticos, sem montar Editais; e todo número do
  consolidado é, por construção, soma de números da `099` (SC-939).
- **Alternatives considered**: leituras em lote por `edital__in` — ficam como saída se a medição
  reprovar o custo linear (R-006), e sob as mesmas regras.

## R-003 — O conjunto viaja no formulário e se resolve na consulta

- **Decision**: parâmetros GET `criterio` (`publicacao`, `numero`, `manual`), `inicio` e `fim`
  (datas, para `publicacao`), `atalho` (`ano`, `s1`, `s2`), `ano`, `busca` (para `manual`),
  `escolha=1` e `edital` repetido (os marcados). A primeira publicação sai de **uma** consulta:
  `Publicacao` com `publication_order = 1` dos Editais do escopo, com `published_at` no intervalo, em
  horário institucional. Sem `escolha=1`, entram todos os elegíveis do critério; com ele, só os
  marcados, e o relatório diz os retirados (do critério e não marcados) e os acrescentados.
- **Elegíveis**: publicados, encerrados ou cancelados **com** primeira publicação. Os demais do
  critério (só existem no critério por número e na escolha manual) são "fora do conjunto", com o
  estado como motivo.
- **Escopo**: toda consulta filtra `institution_scope=ator.institution_scope`; identificador alheio
  ou inexistente simplesmente não volta (FR-2555).
- **Rationale**: nada é gravado; o mesmo endereço reproduz a escolha; o POST da emissão leva os mesmos
  campos.
- **Alternatives considered**: guardar a seleção na sessão — estado invisível e que envelhece; tabela
  de "relatórios salvos" — fora do MVP.

## R-004 — Um instante para o conjunto inteiro

- **Decision**: a leitura de todos os Editais acontece dentro de uma única `leitura_consistente()`
  (`REPEATABLE READ` na transação de fora), e `agora` é tomado uma vez.
- **Rationale**: FR-2564. Uma transação de leitura não sofre falha de serialização; na emissão, que
  grava o evento, a falha é tratada como na `099` ("tente de novo").

## R-005 — A emissão é da Unidade

- **Decision**: na transação da leitura, `Unidade.objects.select_for_update()` na unidade do escopo;
  o número é a contagem de `RegistroAuditoria` com `aggregate_type="Unidade"`, o id dela e a operação
  `EMITIR_RELATORIO_CONSOLIDADO`, mais um; o evento grava em `detalhe` o critério, os ids e
  número/ano dos incluídos, retirados e fora, o instante, o número e o SHA-256. `record_event` recebe
  `new_state=""` e `new_revision=None`, porque a Unidade não tem estado nem revisão.
- **Rationale**: o relatório é da unidade, e não de um Edital; a trava da linha é o idioma do projeto
  (R-003 da `099`). Sem tabela nova (D-005 da `099`).
- **Alternatives considered**: numerar por ator — duas pessoas da mesma unidade teriam "emissão nº 1"
  de documentos diferentes.

## R-006 — O limite de Editais por emissão é medido

- **Decision**: `LIMITE_DE_EDITAIS = 60`, provisório, confirmado pela medição da tarefa de orçamento:
  conjunto de Editais do cenário coerente, consultas por Edital constantes (igualdade entre 1, 2 e 3
  Editais) e tempo de um conjunto grande registrado, sem asserção de tempo — oscila sob carga
  (CLAUDE.md, "Um teste de tempo oscila sob carga").
- **Rationale**: a emissão é síncrona (não há fila, e a Constituição exige necessidade demonstrável
  para criar uma). O limite protege o tempo de resposta e é dito ao usuário.

## R-007 — Privacidade: supressão complementar no Perfil, exclusão no Edital

- **Decision**: uma função pura, `omitidos_por_complemento(populacoes, limiar)`, devolve os grupos
  omitidos e se o total também o é: parte dos grupos abaixo do limiar; enquanto eles somam menos que
  o limiar e há outros, acrescenta o de menor população (desempate pelo identificador); se todos
  entram e a soma não chega ao limiar, o total é omitido. A `099` a usa sobre os Perfis (FR-2587). No
  consolidado, o Edital cujos fatos dizem "total omitido" não entra em número não público nenhum
  (FR-2592), e a base diz quantos.
- **Rationale**: D-006. A exclusão no consolidado resiste à diferença entre duas emissões, que a
  supressão dentro de um documento não alcança.
- **Alternatives considered**: omitir o detalhe de todos os Perfis quando um é pequeno — perde
  detalhe demais; supressão complementar também no consolidado — não protege entre emissões.

## R-008 — Perfil sem inscrição não deve resultado

- **Decision**: em `fatos_do_edital`, marco de Perfil com zero inscrições enviadas, período não
  aberto, sem publicação e sem ato de ordenação vigente não gera pendência nem entra na contagem de
  resultados previstos; a classificação do Perfil diz "não se aplica: nenhuma inscrição enviada".
- **Rationale**: D-007; achado 2 do estudo, confirmado na leitura de `classificacao/application/`: nada
  obriga a emitir ordem para Perfil vazio.

## R-009 — A trilha é dita pelo que registra

- **Decision**: o ponto de atenção da `099` passa de "Houve N registros depois do encerramento" para
  "A trilha de auditoria tem N registros depois do encerramento", e o anexo diz que a contagem cobre
  os atos registrados na trilha. O consolidado usa a mesma frase.
- **Rationale**: FR-2581. A contagem de `relatorio_trilha.posteriores` é de registros de auditoria, e
  ato que não é auditado não aparece.

## R-010 — Onde mora

- **Decision**: `interface/relatorio_consolidado.py` (conjunto, leitura, soma, frases),
  `interface/relatorio_consolidado_pdf.py` (composição) e as views em `interface/relatorio.py`, ao
  lado das da `099`, com quem compartilham o tratamento de concorrência e de caractere sem grafia.
- **Rationale**: as leituras consumidas moram em `interface/` (R-001 da `099`).

## R-011 — O documento usa o escritor da `099`, e a série é tabela

- **Decision**: a composição reaproveita os auxiliares de `relatorio_pdf` e de
  `publicacoes/infrastructure/pdf.py` (`Composicao`, `_tabela`, `Navegacao`, `_arquivo_do_edital`).
  A série de envios é uma tabela por mês, título "Inscrições enviadas, por mês do envio".
- **Rationale**: o motor não desenha gráfico (FR-2536 da `099`); a tabela é o próprio equivalente
  textual. O título não diz "no semestre" porque os meses podem passar do período (FR-2578).

## R-012 — A fixture monta vários Editais coerentes

- **Decision**: `montar_cenario(..., numero="61", publicado_em=None)`. O número entra nos
  identificadores do conteúdo (como o semeador já faz), nas chaves de idempotência e no código do
  Processo; `publicado_em` muda só o instante da publicação, preservando o resto da história. Os
  valores padrão reproduzem o cenário atual, e os testes da `099` não mudam.
- **Rationale**: o consolidado precisa de Editais com o ciclo inteiro, publicados em semestres
  diferentes; um segundo construtor de cenário envelheceria separado deste.
