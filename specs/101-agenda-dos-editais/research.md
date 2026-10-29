# Research: Agenda dos Editais

A descoberta está no estudo
([`doc/estudo-calendario-institucional-2026-10-29.md`](../../doc/estudo-calendario-institucional-2026-10-29.md)),
seções A.1 a A.9. Aqui ficam só as decisões técnicas que a implementação precisa, cada uma com o que
foi verificado no código em 29/10/2026. Caminhos relativos a `backend/processo_seletivo/`.

## R-001 — A fonte é `versoes_vigentes`, e não `EventoCronograma`

- **Decision**: ler o cronograma de `VersaoConsolidada.content["schedule"]` das versões que
  `publicacoes/application/selectors.py::versoes_vigentes(edital_ids=, at=agora)` devolve.
- **Rationale**: a Retificação grava na versão consolidada e não escreve de volta em
  `EventoCronograma`; Evento acrescentado por Retificação não tem linha
  (`comissoes/domain/etapas.py::evento_vigente`, docstring). `versoes_vigentes` é a forma em lote de
  `effective_version`, com a mesma regra de desempate, em duas consultas — a Visão Geral a usa.
- **Alternatives considered**: `EventoCronograma` (diverge depois de Retificação — recusado);
  `effective_version` por Edital (uma consulta por Edital — recusado); tabela de projeção (segunda
  fonte de datas, D-001 — recusado).

## R-002 — O corte relacional: escopo e situação

- **Decision**: `Edital.objects.filter(institution_scope=ator.institution_scope,
  status__in=[PUBLICADO, ENCERRADO]).select_related("processo")`. Sem corte por ano.
- **Rationale**: o escopo vem da consulta, como em toda listagem da gestão (`views.visao_geral`,
  docstring). Cancelado sai (D-009, como `selecoes_publicas`). Em elaboração, revisão e homologado
  não têm versão vigente, e saem de qualquer jeito; filtrá-los na consulta poupa o lote. O ano não
  corta porque período atravessa o ano.
- **Alternatives considered**: corte pelo ano do número (perderia o Edital de 2025 com marco em
  2026).

## R-003 — O aviso de Retificação a vigorar: uma consulta agregada

- **Decision**: `VersaoConsolidada.objects.filter(edital_id__in=ids, valid_from__gt=agora)
  .values("edital_id").annotate(vigora_em=Min("valid_from"))`.
- **Rationale**: a vigência futura é exatamente `valid_from > agora` (`retificacoes.py`, a
  consolidação materializa a versão com `valid_from` igual à vigência). `Min` dá a primeira a
  vigorar. Uma consulta, portátil entre PostgreSQL e SQLite, sem materializar conteúdo.
- **Alternatives considered**: comparar o cronograma futuro com o vigente para avisar só quando a
  data muda (exige materializar o conteúdo futuro, e a pessoa precisa saber da Retificação de
  qualquer modo — recusado).

## R-004 — O custo do conteúdo inteiro

- **Decision**: manter `versoes_vigentes` como está e **medir** na implementação o tempo da página
  e o volume do conteúdo com dezenas de Editais publicados. Se a medição mostrar problema, a menor
  otimização é uma variante que materialize só `content__schedule` (transformação de chave do
  `JSONField`, portátil), e não tabela nem cache.
- **Rationale**: a Visão Geral já paga o mesmo custo; otimizar sem medir seria a infraestrutura
  prematura que a autorização recusa.
- **Alternatives considered**: `.only()`/`defer("content")` (o conteúdo é o que se lê);
  filtro de janela em JSONB (só PostgreSQL, quebra o modo SQLite da suíte).
- **Resultado da medição**: registrado em [quickstart.md](quickstart.md), seção *Desempenho*.

## R-005 — Marco pontual × período: a régua do relatório do Edital

- **Decision**: período é Evento com término em **outro dia** que o início, ambos lidos na `ZONA`;
  os demais são pontuais. O período de inscrições sem término é período aberto (só abertura).
- **Rationale**: é a régua de `interface/relatorio_do_edital.py::_cronograma` (`periodo`); a régua
  do período (`inscricoes/domain/periodo.py`) diz que o período sem término segue aberto.
- **Alternatives considered**: período = qualquer Evento com término (a prova das 8h às 12h viraria
  abertura e encerramento no mesmo dia — recusado).

## R-006 — A fase, e como ela é dita

- **Decision**: a fase vem de `editais/domain/fase_do_evento.py::fase_do_evento(evento, conteudo,
  agora)`; o marco **de abertura** e **de encerramento** de um período têm, além da fase do
  período, a sua própria posição no tempo (`calendario.fase(instante, None)`). A tradução para a
  tela é: `PLANEJADO` → *por vir* (sem rótulo), `EM_ANDAMENTO` → *em curso pelo cronograma*,
  `CONCLUIDO` → *data passada*; cancelado → *Cancelado*.
- **Rationale**: a régua é única e não se copia (`028`, `047`); a tradução é de apresentação, e é o
  que D-006 exige: data passada não prova execução.
- **Alternatives considered**: usar o `✓` e o "concluído" do portal (afirmaria execução — recusado).

## R-007 — A espécie do Evento

- **Decision**: `inscricoes` quando `isRegistrationPeriod` é verdadeiro; senão `etapa` quando algum
  `stages[].scheduleEventId` do mesmo conteúdo aponta o Evento; senão `demais`.
- **Rationale**: as duas marcas são estruturais e publicadas; nenhuma vem de texto. A precedência
  do período foi registrada nas Clarifications da spec.

## R-008 — As semanas do mês

- **Decision**: `calendar.Calendar(firstweekday=6).monthdatescalendar(ano, mes)`; o dia de fora do
  mês vira célula vazia.
- **Rationale**: biblioteca padrão, testada, sem dependência; domingo primeiro (D-010). Verificado:
  fevereiro de 2026 dá 4 semanas, agosto de 2026 dá 6, novembro de 2026 dá 5.

## R-009 — Parâmetros e padrões

- **Decision**: `visao` (`mes` | `proximos`; padrão `mes`), `mes` (`AAAA-MM`; padrão o corrente na
  `ZONA`), `dia` (`AAAA-MM-DD`; só na visão do mês), `janela` (`7` | `30`; padrão `7`), `edital`
  (UUID), `especie` (`inscricoes` | `etapa` | `demais`). Valor inválido cai no padrão, sem erro e
  sem 404.
- **Rationale**: listagem não tem 404 de escopo (`views.visao_geral`); estado inteiro no endereço
  (FR-2638). Sem `raise Http404`, a view não entra no inventário de negativas da `033`.

## R-010 — Filtros em memória, opções estáveis

- **Decision**: filtros aplicados sobre os marcos já projetados; as opções de Edital são os Editais
  considerados com algum Evento no cronograma vigente, em ordem de ano e número — as mesmas nas duas
  visualizações, para que trocar de aba não faça a opção sumir.
- **Rationale**: nenhuma consulta a mais (padrão da vitrine na `024`); um identificador de outro
  escopo não está entre os carregados e simplesmente não casa (FR-2610).

## R-011 — A grade a 375 px e o destaque

- **Decision**: `<table>` com `table-layout:fixed`, sete colunas iguais; abaixo de 60rem os nomes
  ficam ocultos (`display:none`) e a célula mostra o dia e a contagem. O destaque usa o par já
  existente `--verde-escuro` sobre `--verde-claro` (em `PARES` do teste de contraste) mais negrito e
  borda — a contagem escrita é o sinal que não depende de cor.
- **Rationale**: 375 − 2 × 16 = 343 px, ~49 px por coluna; o alvo de toque é a célula inteira. Par
  existente evita cor nova não verificada.

## R-012 — Os destinos dos links

- **Decision**: *Edital* → `interface:detalhe` (página do Edital na gestão); *Cronograma publicado*
  → `portal:selecao` + `#cronograma-titulo` (a seção do cronograma na página pública).
- **Rationale**: a página do Edital na gestão não tem seção de cronograma; a pública tem, com
  âncora estável. O `<li>` do Evento no portal não tem `id`, e acrescentá-lo é a fase 1.1 do estudo.

## R-013 — O indicador de períodos é contado da mesma lista de períodos

- **Decision**: `semanas_do_mes` recebe também os períodos já projetados (os mesmos da lista do mês,
  depois dos filtros) e conta, para cada dia, os que o abrangem (`Periodo.abrange(dia)`: do dia de
  início ao de término, inclusive; sem término, de início em diante). O dia consultado lista
  exatamente os períodos com `abrange(dia)`, e por isso as duas contagens não têm como divergir.
- **Rationale**: nenhuma consulta nova; nenhuma forma nova persistida; a mesma função de pertinência
  serve à célula e ao dia (SC-959). Cancelados e encerrados já saem em `periodos_do_conteudo`.
- **Custo**: até ~30 períodos × 42 células por mês — desprezível perto da leitura.
- **Alternatives considered**: materializar um item por dia (recusado: é o que `D-002` proíbe);
  contar só os dias do meio (recusado: o usuário pediu os intervalos que **abrangem** o dia).

## R-014 — A forma do indicador

- **Decision**: na célula, abaixo da quantidade de marcos, `<span class="periodos-do-dia">` com uma
  barra horizontal desenhada por borda (a forma de um intervalo) e o número; em tela larga, o texto
  *N períodos*; no estreito, só a barra e o número, com o texto completo para leitor de tela. Cor de
  apoio (`--texto-fraco`), para não competir com o verde dos marcos. Uma legenda curta junto da
  grade nomeia as duas marcas.
- **Rationale**: distinguir por forma e texto, e não por cor (FR-2670); 375 px já está no limite.
